from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.config import ManageInvoices
from bika.lims.utils import t
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from bika.lims.browser import BrowserView
from zope.interface import implements
import plone
import json
from bika.lims.permissions import *
from Products.CMFCore.utils import getToolByName


class ClientBatchesView(BikaListingView):

    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(ClientBatchesView, self).__init__(context, request)
        self.catalog = 'bika_catalog'
        self.contentFilter = {
            'portal_type': 'Batch',
            'cancellation_state': 'active',
	     'path': {
                "query": "/".join(context.getPhysicalPath()),
                "level": 0
            }
        }
	
        self.icon = self.portal_url + "/++resource++bika.lims.images/batch_big.png"
        self.title = self.context.translate(_("Batches"))
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title')},
            'BatchID': {'title': _('Batch ID')},
            'Description': {'title': _('Description')},
            'BatchDate': {'title': _('Date of creation')},
	    'BatchTimeLeft': {'title': _('Time left')},
            'state_title': {'title': _('State'), 'sortable': False},
        }

        self.review_states = [  # leave these titles and ids alone
            {'id': 'default',
             'contentFilter': {'review_state': 'open'},
             'title': _('Open'),
             'transitions': [{'id': 'close'}, {'id': 'cancel'}, {'id': 'send'}],
             'columns': ['Title',
                         'BatchID',
                         'BatchDate',
			 'BatchTimeLeft',
                         'Description',
                         'state_title', ]
             },
	     {'id': 'due',
             'contentFilter': {'review_state': 'due'},
             'title': _('due'),
             'transitions': [{'id': 'receive'}, {'id': 'cancel'}],
             'columns': ['Title',
                         'BatchID',
                         'BatchDate',
			 'BatchTimeLeft',
                         'Description',
                         'state_title', ]
             },
	    {'id': 'received',
             'contentFilter': {'review_state': 'received'},
             'title': _('received'),
             'transitions': [{'id': 'publish'}],
             'columns': ['Title',
                         'BatchID',
                         'BatchDate',
			 'BatchTimeLeft',
                         'Description',
                         'state_title', ]
             },
	    {'id': 'published',
             'contentFilter': {'review_state': 'published'},
             'title': _('published'),
             'transitions': [{'id': 'republish'},{'id': 'close'}],
             'columns': ['Title',
                         'BatchID',
                         'BatchDate',
			 'BatchTimeLeft',
                         'Description',
                         'state_title', ]
             },
            {'id': 'closed',
             'contentFilter': {'review_state': 'closed'},
             'title': _('Closed'),
             'transitions': [{'id': 'open'}],
             'columns': ['Title',
                         'BatchID',
                         'BatchDate',
			 'BatchTimeLeft',
                         'Description',
                         'state_title', ]
             },
            {'id': 'cancelled',
             'title': _('Cancelled'),
             'transitions': [{'id': 'reinstate'}],
             'contentFilter': {'cancellation_state': 'cancelled'},
             'columns': ['Title',
                         'BatchID',
                         'BatchDate',
			 'BatchTimeLeft',
                         'Description',
                         'state_title', ]
             },
            {'id': 'all',
             'title': _('All'),
             'transitions': [],
             'columns': ['Title',
                         'BatchID',
                         'BatchDate',
		         'BatchTimeLeft',
                         'Description',
                         'state_title', ]
             },
        ]

    def __call__(self):
        #print "call ClientBatchesView call() "
	mtool = getToolByName(self.context, 'portal_membership')
	print "permission to add batch:"+str(mtool.checkPermission(AddBatch, self.context))
	if mtool.checkPermission(AddBatch, self.context):
		self.context_actions = {
		    _('Add'):
		        {'url': 'createObject?type_name=Batch',
		         'icon': '++resource++bika.lims.images/add.png'}}

        return super(ClientBatchesView, self).__call__()

    def isItemAllowed(self, obj):
        """
        It checks if the item can be added to the list depending on the
        department filter. If the batch contains analysis requests
        with services from the selected department, show it.
        If department filtering is disabled in bika_setup, will return True.
        @obj: it is a batch.
        @return: boolean
        """
        if not self.context.bika_setup.getAllowDepartmentFiltering():
            return True
        # Gettin the departments from the batch
        ars = obj.getAnalysisRequests()
        # Getting the cookie value
        cookie_dep_uid = self.request.get('filter_by_department_info', '')
        filter_uids = set(
            cookie_dep_uid.split(','))
        for ar in ars:
            # Comparing departments' UIDs
            deps_uids = set(ar.getDepartmentUIDs())
            matches = deps_uids & filter_uids
            if len(matches) > 0:
                return True
        return False

    def folderitems(self):
        self.filter_indexes = None

        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']

            bid = obj.getBatchID()
            items[x]['BatchID'] = bid
            items[x]['replace']['BatchID'] = "<a href='%s/%s'>%s</a>" % (items[x]['url'], 'analysisrequests', bid)

            title = obj.Title()
            items[x]['Title'] = title
            items[x]['replace']['Title'] = "<a href='%s/%s'>%s</a>" % (items[x]['url'], 'analysisrequests', title)

            if obj.getClient():
                items[x]['Client'] = obj.getClient().Title()
                items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % ( obj.getClient().absolute_url(), obj.getClient().Title())
            else:
                items[x]['Client'] = ''

            date = obj.Schema().getField('BatchDate').get(obj)
            if callable(date):
                date = date()
            items[x]['BatchDate'] = date
            items[x]['replace']['BatchDate'] = self.ulocalized_time(date)

        return items


class ajaxGetBatches(BrowserView):

    """ Vocabulary source for jquery combo dropdown box
    """

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']

        rows = []

        batches = self.bika_catalog(portal_type='Batch')

        for batch in batches:
            batch = batch.getObject()
            if self.portal_workflow.getInfoFor(batch, 'review_state', 'open') != 'open' \
               or self.portal_workflow.getInfoFor(batch, 'cancellation_state') == 'cancelled':
                continue
            if batch.Title().lower().find(searchTerm) > -1 \
            or batch.Description().lower().find(searchTerm) > -1:
                rows.append({'BatchID': batch.getBatchID(),
                             'Description': batch.Description(),
                             'BatchUID': batch.UID()})

        rows = sorted(rows, cmp=lambda x, y: cmp(x.lower(), y.lower()), key=itemgetter(sidx and sidx or 'BatchID'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}

        return json.dumps(ret)
