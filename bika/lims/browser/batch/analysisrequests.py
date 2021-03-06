# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from operator import itemgetter
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.analysisrequest import AnalysisRequestAddView as _ARAV
from bika.lims.browser.analysisrequest import AnalysisRequestsView as _ARV
from bika.lims.permissions import *
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements



class AnalysisRequestsView(_ARV, _ARAV):

    ar_add = ViewPageTemplateFile("../analysisrequest/templates/ar_add.pt")
    implements(IViewView)

    def __init__(self, context, request):
	self.ar_count=10
        super(AnalysisRequestsView, self).__init__(context, request)

    def contentsMethod(self, contentFilter):
        return self.context.getAnalysisRequests(**contentFilter)

    def __call__(self):
        self.context_actions = {}
	print "context"+str(self.context)
        mtool = getToolByName(self.context, 'portal_membership')
	print "===="+str(mtool.checkPermission(AddAnalysisRequest,self.portal))+"======="+str(mtool)
       
        if mtool.checkPermission(AddAnalysisRequest, self.portal):
            self.context_actions[self.context.translate(_('Add new'))] = {
                'url': self.context.absolute_url() + \
                    "/portal_factory/"
                    "AnalysisRequest/Request new analyses/ar_add?batch="+self.context.UID()+"&ar_count=1",
                'icon': '++resource++bika.lims.images/add.png'}
        return super(AnalysisRequestsView, self).__call__()

    def getMemberDiscountApplies(self):
        client = self.context.getClient()
        return client and client.getMemberDiscountApplies() or False

    def getRestrictedCategories(self):
        client = self.context.getClient()
        return client and client.getRestrictedCategories() or []

    def getDefaultCategories(self):
        client = self.context.getClient()
        return client and client.getDefaultCategories() or []
