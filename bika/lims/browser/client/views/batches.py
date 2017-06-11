# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims.browser.batchfolder import BatchFolderContentsView
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import isActive
from bika.lims.permissions import AddBatch


class ClientBatchesView(BatchFolderContentsView):
    

    def __init__(self, context, request):
       super(ClientBatchesView, self).__init__(context, request)
       self.view_url = self.context.absolute_url() + "/batches"

       """Remove Client column """
       review_states = []
       for review_state in self.review_states:
            review_state['columns'].remove('Client')
            review_states.append(review_state)
       self.review_states = review_states



    def __call__(self):
	wf = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')
        addPortalMessage = self.context.plone_utils.addPortalMessage
        translate = self.context.translate
        # client contact required
        active_contacts = [c for c in self.context.objectValues('Contact') if
                           wf.getInfoFor(c, 'inactive_state', '') == 'active']
        if isActive(self.context):
            if self.context.portal_type == "Client" and not active_contacts:
                msg = _(
                    "Client contact required before request may be submitted")
                addPortalMessage(msg)
            else:
                if mtool.checkPermission(AddBatch, self.context):
                    self.context_actions[_('Add')] = \
		{'url': 'createObject?type_name=Batch',
                 'icon': self.portal.absolute_url() + '/++resource++bika.lims.images/add.png'}

	"""
	print"=================================="
	bc = getToolByName(self.context, "bika_catalog")
	for b in bc(portal_type='Batch'):
            batch = b.getObject()
	    if batch.getClientUID()==self.context.UID():
		    print "contexte :"+self.context.UID()
		    print "client   :"+batch.getClientUID()
		    print "title :"+batch.getClientTitle()
		    print "title :"+batch.Title()
            #print "batch"+b
	print"=================================="
	"""
        return BatchFolderContentsView.__call__(self)



    def contentsMethod(self, contentFilter):
        bc = getToolByName(self.context, "bika_catalog")
	batches = {}
        for b in bc(portal_type='Batch'):
            batch = b.getObject()
	    if batch.getClientUID()==self.context.UID():
	    	batches[batch.UID()] = batch
        return batches.values()
