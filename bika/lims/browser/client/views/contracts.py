from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IContracts
from bika.lims.vocabularies import CatalogVocabulary

from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from plone.supermodel import model
from plone.dexterity.content import Container


class ClientContractsView(BikaListingView):
    implements(IFolderContentsView,IViewView)

    def __init__(self, context, request):
        super(ClientContractsView, self).__init__(context, request)
        
	self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'Contract',
            'sort_on': 'sortable_title',
	    'path': {
                "query": "/".join(context.getPhysicalPath()),
                "level": 0}
        }
	
        self.title = self.context.translate(_("Contracts"))
        self.context_actions = {
            _('Add'): {'url': '++add++Contract',  # To work with dexterity
                       'icon': '++resource++bika.lims.images/add.png'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "Contract"
        self.icon = self.portal_url + "/++resource++bika.lims.images/contracts.png"
        self.description = ""
	
        self.columns = {
            'title': {'title': _('title'),
                      'sortable': True,
                      'toggle': True,
                      'replace_url': 'absolute_url'},
	    'representant_center': {'title': _('Representant du Centre'),
				    'replace_url': 'absolute_url'},
	    'representant_client': {'title': _('Representant du Client'),
				    'replace_url': 'absolute_url'},
            'publishing_date': {'title': _('Publishing Date'),
				    'replace_url': 'absolute_url'},
	    'expiration_date': {'title': _('Expiration Date'),
				    'replace_url': 'absolute_url'}
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['title','representant_center','representant_client','publishing_date','expiration_date']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['title','representant_center','representant_client','publishing_date','expiration_date']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['title','representant_center','representant_client','publishing_date','expiration_date']},
        ]


class ContractImputationsView(BikaListingView):
    
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
	super(ContractImputationsView, self).__init__(context, request)
        
	self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'Imputation',
            'sort_on': 'sortable_title',
	    'path': {
                "query": "/".join(context.getPhysicalPath()),
                "level": 0}
        }
	
        self.title = self.context.translate(_("Imputations"))
        self.context_actions = {
            _('Add'): {'url': '++add++Imputation',  # To work with dexterity
                       'icon': '++resource++bika.lims.images/add.png'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "Imputation"
        self.icon = self.portal_url + "/++resource++bika.lims.images/contracts.png"
        self.description = ""
	
        self.columns = {
            'number': {'title': _('number'),
                      'sortable': True,
                      'toggle': True,
                      'replace_url': 'absolute_url'},
            'title': {'title': _('designation'),	
		      'replace_url': 'absolute_url'},
	    'delais_stock': {'title': _('delais stock'),	
		      'replace_url': 'absolute_url'}
        }
       
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['number',
                         'title',
			 'delais_stock'
                         ]
	    },
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['number',
                         'title',
		         'delais_stock'
                         ]
	    },
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['number',
                         'title',
			 'delais_stock',
                         ]
	    },
        ]
