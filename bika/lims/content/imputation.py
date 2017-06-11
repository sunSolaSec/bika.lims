from bika.lims import _
from plone.supermodel import model
from plone import api
from zope import schema
from plone.dexterity.content import Item
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IContextSourceBinder
from datetime import date
from Products.CMFCore.permissions import ModifyPortalContent, AddPortalContent

class AnalysisProfiles(object):
    """Context source binder to provide a vocabulary of analysis profil.
    """
    implements(IContextSourceBinder)

    def __call__(self, context):
        catalog_name = 'portal_catalog'
        contentFilter = {'portal_type': 'AnalysisProfile',
                         'inactive_state': 'active'
		}
       #in Add caction context==container
	#   but in Edit action the context!=container
	#	so clients contact are not displayed in edit page
	#	Solution:
	if str(context).startswith("<Imputa"):
	    print "change Contexte :"+str(context)
	    c=context.aq_parent.aq_parent
	    print "To :"+str(c)
	else:
	    c=context.aq_parent
	
	catalog = getToolByName(c, catalog_name)
        brains = catalog(contentFilter)
	#print brains
        terms = []
	
	for brain in brains:
	    container = brain.getObject().aq_parent
            # Show only the client and lab's Contact
	    if container.portal_type == 'Client' and container != c:
                continue
            art_uid = brain.UID
            title = brain.Title
            terms.append(SimpleVocabulary.createTerm(art_uid, str(art_uid), title))
        return SimpleVocabulary(terms)



class ContactsP(object):
    """Context source binder to provide a vocabulary of clients contacts.
    """
    implements(IContextSourceBinder)

    def __call__(self, context):

	catalog_name = 'portal_catalog'
        contentFilter = {'portal_type': 'Contact',
                         'inactive_state': 'active'}
	#in Add caction context==container
	#   but in Edit action the context!=container
	#	so clients contact are not displayed in edit page
	#	Solution:
	if str(context).startswith("<Imputa"):
	    print "change Contexte :"+str(context)
	    c=context.aq_parent.aq_parent
	    print "To :"+str(c)
	else:
	    c=context.aq_parent
	
	catalog = getToolByName(c, catalog_name)
        brains = catalog(contentFilter)
	#print brains
        terms = []
	
	for brain in brains:
	    container = brain.getObject().aq_parent
            # Show only the client and lab's Contact
	    if container.portal_type == 'Client' and container != c:
                continue
            art_uid = brain.UID
            title = brain.Title
            terms.append(SimpleVocabulary.createTerm(art_uid, str(art_uid), title))
        return SimpleVocabulary(terms)

class ContactsS(object):
    """provide a vocabulary of lab contacts.
    """
    implements(IContextSourceBinder)

    def __call__(self, context):

	catalog_name = 'portal_catalog'
        contentFilter = {'portal_type': 'LabContact',
                         'inactive_state': 'active'}
	catalog = getToolByName(context, catalog_name)
        brains = catalog(contentFilter)
	terms = []
	
	for brain in brains:
	    art_uid = brain.UID
            title = brain.Title
            terms.append(SimpleVocabulary.createTerm(art_uid, str(art_uid), title))
        return SimpleVocabulary(terms)


class IImputation(model.Schema):
        """A Imputation interface
        """

        title = schema.TextLine(
                title=_(u"Number"),
                description=_(u""),
                required=True
                )

        number = schema.Text(
                title=_(u"number"),
                description=_(u""),
                required=True
                )

        projet = schema.Text(
                title=_(u"Projet"),
                description=_(u""),
                required=False,
                )
	delais_stock = schema.Int(
            title=_(u'Delais du stock par mois')
        )
	analysis_profiles = schema.List(
            title=_(u'Analysis Profil'),
            value_type=schema.Choice(
		source=AnalysisProfiles()
	    )
        )
	
	contacts_p = schema.List(
            title=_(u'Principale distination'),
            value_type=schema.Choice(
                source=ContactsP()
            )
        )
	contacts_s = schema.List(
            title=_(u'Second distination'),
            value_type=schema.Choice(
                source=ContactsS()
            )
        )
	
class Imputation(Item):
    
    implements(IImputation)



