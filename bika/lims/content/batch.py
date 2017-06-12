# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IBatch, IClient
from bika.lims.workflow import skip, BatchState, StateFlow, getCurrentState,\
    CancellationState
from bika.lims.browser.widgets import DateTimeWidget
from plone import api
from plone.app.folder.folder import ATFolder
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements
from bika.lims.permissions import EditBatch
from plone.indexer import indexer
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.ateapi import RecordsField
from bika.lims.browser.widgets import RecordsWidget as bikaRecordsWidget
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets.durationwidget import DurationWidget

from bika.lims.browser.widgets import ReferenceWidget
from DateTime import DateTime

from Products.CMFCore import permissions
from Products.CMFCore.permissions import View
import sys



class InheritedObjectsUIField(RecordsField):

    """XXX bika.lims.RecordsWidget doesn't cater for multiValued fields
    InheritedObjectsUI is a RecordsField because we want the RecordsWidget,
    but the values are stored in ReferenceField 'InheritedObjects'
    """

    def get(self, instance, **kwargs):
        # Return the formatted contents of InheritedObjects field.
        field = instance.Schema()['InheritedObjects']
        value = field.get(instance)
        return [{'Title': x.Title(),
                 'ObjectID': x.id,
                 'Description': x.Description()} for x in value]

    def getRaw(self, instance, **kwargs):
        # Return the formatted contents of InheritedObjects field.
        field = instance.Schema()['InheritedObjects']
        value = field.get(instance)
        return [{'Title': x.Title(),
                 'ObjectID': x.id,
                 'Description': x.Description()} for x in value]

    def set(self, instance, value, **kwargs):
        _field = instance.Schema().getField('InheritedObjects')
        uids = []
        if value:
            bc = getToolByName(instance, 'bika_catalog')
            ids = [x['ObjectID'] for x in value]
            if ids:
                proxies = bc(id=ids)
                if proxies:
                    uids = [x.UID for x in proxies]
        RecordsField.set(self, instance, value)
        return _field.set(instance, uids)


    


schema = BikaFolderSchema.copy() + Schema((

     ReferenceField(
        'Client',
        required=1,
        allowed_types=('Client',),
        relationship='BatchClient',
	widget=ReferenceWidget(
            label=_("Client"),
            size=40,
            visible=True,
            base_query={'inactive_state': 'active'},
            showOn=True,
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Title', 'width': '60', 'label': _('Title')},
                      {'columnName': 'ClientID', 'width': '20', 'label': _('Client ID')}
                     ],
      ),
    ),

    ComputedField(
        'ClientUID',
        searchable=True,
        expression='here.getClient().UID()',        
	widget=ComputedWidget(
            visible=False,
        ),
    ),

    ReferenceField(
        'Contact',
        required=0,
        default_method='getContactUIDForUser',
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('Contact',),
        referenceClass=HoldingReference,
        relationship='BatchContact',
        mode="rw",
        read_permission=permissions.View,
        widget=ReferenceWidget(
            label=_("Contact"),
            size=40,
            helper_js=("bika_widgets/referencewidget.js",
                       "++resource++bika.lims.js/contact.js"),
            visible=True,
            showOn=True,
            popup_width='400px',
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'Fullname', 'width': '50',
                       'label': _('Name')},
                      {'columnName': 'EmailAddress', 'width': '50',
                       'label': _('Email Address')},
                      ],
        ),
    ),
    ReferenceField(
        'Imputation',
        required=0,
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('Imputation'),
        relationship='BatchImputation',
        mode="rw",
        read_permission=permissions.View,
        widget=ReferenceWidget(
            label=_("Imputation"),
            size=40,
            visible=True,
            showOn=True,
            popup_width='400px',
            colModel=[{'columnName': 'UID', 'hidden': True},
                      {'columnName': 'number', 'width': '50',
                       'label': _('number')},
                      ],
        ),
    ),

    DateTimeField(
        'BatchDate',
        required=False,
	default_method = 'current_date',
	widget=DateTimeWidget(
            label=_('Date of creation'),
	    size=40,
	    visible=True
        ),
    ),
    
    DateTimeField(
        'BatchDateLimit',
        required=False,
	widget=DateTimeWidget(
            label=_('Date limit pour le stockage'),
	    size=40,
        ),
    ),

    StringField(
        'BatchID',
        searchable=True,
        mode="rw",
        expression='self.getId()',
        widget=StringWidget(
            label=_("Batch ID"),
	    visible=True,
	    size=40,
        )
    ),
   
    StringField(
        'ClientBatchID',
        searchable=True,
        required=0,
        widget=StringWidget(
            label=_("Client ID"),
	    visible=True,
	    size=40,
        )
    ),

    LinesField(
        'BatchLabels',
        vocabulary="BatchLabelVocabulary",
        accessor="getLabelNames",
        widget=MultiSelectionWidget(
            label=_("Batch Labels"),
            format="checkbox",
	    visible=False,
        )
    ),
    TextField(
        'Remarks',
        searchable=True,
        default_content_type='text/x-web-intelligent',
        allowable_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_('Remarks'),
            append_only=True,
        )
    ),
    ReferenceField(
        'InheritedObjects',
        required=0,
        multiValued=True,
        allowed_types=('AnalysisRequest'),  # batches are expanded on save
        referenceClass = HoldingReference,
        relationship = 'BatchInheritedObjects',
        widget=ReferenceWidget(
            visible=False,
        ),
    ),
    InheritedObjectsUIField(
        'InheritedObjectsUI',
        required=False,
        type='InheritedObjects',
        subfields=('Title', 'ObjectID', 'Description'),
        subfield_sizes = {'Title': 25,
                          'ObjectID': 25,
                          'Description': 50,
                          },
        subfield_labels = {'Title': _('Title'),
                           'ObjectID': _('Object ID'),
                           'Description': _('Description')
                           },
        widget = bikaRecordsWidget(
            label=_("Inherit From"),
	    visible=False,
            description=_(
                "Include all analysis requests belonging to the selected objects."),
            innerJoin="<br/>",
            combogrid_options={
                'Title': {
                    'colModel': [
                        {'columnName': 'Title', 'width': '25',
                         'label': _('Title'), 'align': 'left'},
                        {'columnName': 'ObjectID', 'width': '25',
                         'label': _('Object ID'), 'align': 'left'},
                        {'columnName': 'Description', 'width': '50',
                         'label': _('Description'), 'align': 'left'},
                        {'columnName': 'UID', 'hidden': True},
                    ],
                    'url': 'getAnalysisContainers',
                    'showOn': False,
                    'width': '600px'
                },
                'ObjectID': {
                    'colModel': [
                        {'columnName': 'Title', 'width': '25',
                         'label': _('Title'), 'align': 'left'},
                        {'columnName': 'ObjectID', 'width': '25',
                         'label': _('Object ID'), 'align': 'left'},
                        {'columnName': 'Description', 'width': '50',
                         'label': _('Description'), 'align': 'left'},
                        {'columnName': 'UID', 'hidden': True},
                    ],
                    'url': 'getAnalysisContainers',
                    'showOn': False,
                    'width': '600px'
                },
            },
        ),
    ),
)
)


schema['title'].required = False
schema['title'].expression = 'self.getId()'
schema['title'].widget.size = 10
schema['description'].widget.visible = False
schema['title'].widget.description = _("the Batch ID will be used by default.")


class Batch(ATFolder):
    implements(IBatch)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    security.declarePublic('current_date')
    def current_date(self):
        return DateTime()

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Batch ID if title is not defined """
        titlefield = self.Schema().getField('title')
        if titlefield.widget.visible:
            return safe_unicode(self.title).encode('utf-8')
        else:
            return safe_unicode(self.id).encode('utf-8')

    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    def getClient(self):
        """ Retrieves the Client for which the current Batch is attached to
            Tries to retrieve the Client from the Schema property, but if not
            found, searches for linked ARs and retrieve the Client from the
            first one. If the Batch has no client, returns None.
        """
        client = self.Schema().getField('Client').get(self)
        if client:
            return client
        client = self.aq_parent
        if IClient.providedBy(client):
            return client

    def getImputation(self):
        client = self.Schema().getField('Client').get(self)
        if client:
            return client
        client = self.aq_parent
        if IClient.providedBy(client):
            return client

    def getClientTitle(self):
        client = self.getClient()
        if client:
            return client.Title()
        return ""

    def getContactTitle(self):
        return ""

    def getProfilesTitle(self):
        return ""

    def getAnalysisCategory(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getCategoryTitle()
            if val not in value:
                value.append(val)
        return value

    def getAnalysisService(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getServiceTitle()
            if val not in value:
                value.append(val)
        return value

    def getAnalysts(self):
        analyses = []
        for ar in self.getAnalysisRequests():
            analyses += list(ar.getAnalyses(full_objects=True))
        value = []
        for analysis in analyses:
            val = analysis.getAnalyst()
            if val not in value:
                value.append(val)
        return value

    security.declarePublic('getBatchID')

    def getBatchID(self):
        #if self.BatchID != '':
         #   return self.BatchID
        return self.getId()

    security.declarePublic('getContactUIDForUser')

    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        pc = getToolByName(self, 'portal_catalog')
        r = pc(portal_type='Contact',
               getUsername=user_id)
        if len(r) == 1:
            return r[0].UID

    def BatchLabelVocabulary(self):
        """ return all batch labels """
        bsc = getToolByName(self, 'bika_setup_catalog')
        ret = []
        for p in bsc(portal_type='BatchLabel',
                     inactive_state='active',
                     sort_on='sortable_title'):
            ret.append((p.UID, p.Title))
        return DisplayList(ret)

    def getAnalysisRequests(self, **kwargs):
        """ Return all the Analysis Requests linked to the Batch
        kargs are passed directly to the catalog.
        """
        query = kwargs
        query['portal_type'] = 'AnalysisRequest'
        query['BatchUID'] = self.UID()
        bc = api.portal.get_tool('bika_catalog')
        brains = bc(query)
        return [b.getObject() for b in brains]

    def isOpen(self):
        """ Returns true if the Batch is in 'open' state
        """
        revstatus = getCurrentState(self, StateFlow.review)
        canstatus = getCurrentState(self, StateFlow.cancellation)
        return revstatus == BatchState.open \
            and canstatus == CancellationState.active

    def getLabelNames(self):
        uc = getToolByName(self, 'uid_catalog')
        uids = [uid for uid in self.Schema().getField('BatchLabels').get(self)]
        labels = [label.getObject().title for label in uc(UID=uids)]
        return labels

    def workflow_guard_open(self):
        """ Permitted if current review_state is 'closed' or 'cancelled'
            The open transition is already controlled by 'Bika: Reopen Batch'
            permission, but left here for security reasons and also for the
            capability of being expanded/overrided by child products or
            instance-specific-needs.
        """
        revstatus = getCurrentState(self, StateFlow.review)
        canstatus = getCurrentState(self, StateFlow.cancellation)
        return revstatus == BatchState.closed \
            and canstatus == CancellationState.active

    def workflow_guard_close(self):
        """ Permitted if current review_state is 'open'.
            The close transition is already controlled by 'Bika: Close Batch'
            permission, but left here for security reasons and also for the
            capability of being expanded/overrided by child products or
            instance-specific needs.
        """
        revstatus = getCurrentState(self, StateFlow.review)
        canstatus = getCurrentState(self, StateFlow.cancellation)
        return revstatus == BatchState.open \
            and canstatus == CancellationState.active
    
    def startDefaultValue():
    	return datetime.datetime.today() + datetime.timedelta(7)



registerType(Batch, PROJECTNAME)


@indexer(IBatch)
def BatchDate(instance):
    return instance.Schema().getField('BatchDate').get(instance)
