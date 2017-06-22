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

from bika.lims.browser.fields import DurationField
from plone.indexer import indexer

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



class ContactsPrincipale(object):
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

class ContactsSecondaire(object):
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
	    cs_uid = brain.UID
            title = brain.Title
	    print  "Title ========"+title+cs_uid 
            terms.append(SimpleVocabulary.createTerm(cs_uid, str(cs_uid), title))
        return SimpleVocabulary(terms)


class IImputation(model.Schema):
        """A Imputation interface
        """

        title = schema.TextLine(
                title=_(u"Designation"),
                description=_(u""),
                required=False
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

	delais_stock =schema.Int(
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
                source=ContactsPrincipale()
            )
        )
	contacts_s = schema.List(
            title=_(u'Second distination'),
            value_type=schema.Choice(
                source=ContactsSecondaire()
            )
        )

@indexer(IImputation)
def cccontacts(obj):
    return obj.cccontacts()

@indexer(IImputation)
def aprofil(obj):
    return obj.aprofil()

@indexer(IImputation)
def ClientUID(obj):
    return obj.getClientUID()
	
class Imputation(Item):
    
    implements(IImputation)

    def aprofil(self):
        l = []
        art_uids = self.analysis_profiles
        # I have to get the catalog in this way because I can't do it with 'self'...
        pc = getToolByName(api.portal.get(), 'uid_catalog')
        for art_uid in art_uids:
            art_obj = pc(UID=art_uid)
            if len(art_obj) != 0:
                l.append((art_obj[0].Title, art_uid))
        return l

    def cccontacts(self):
        l = []
        art_uids = self.contacts_p
	cs_uids = self.contacts_s
        # I have to get the catalog in this way because I can't do it with 'self'...
        pc = getToolByName(api.portal.get(), 'uid_catalog')
        for art_uid in art_uids:
            art_obj = pc(UID=art_uid)
	    if len(art_obj) != 0:
                l.append((art_obj[0].Title, art_uid))
	for cs_uid in cs_uids:
            cs_obj = pc(UID=cs_uid)
	    if len(cs_obj) != 0:
                l.append((cs_obj[0].Title, cs_uid))
        return l
    
    def getClientUID(self):
	print "the client UID is :"+ self.aq_parent.aq_parent.UID()+"="+ self.aq_parent.aq_parent.Title()
        return self.aq_parent.UID()



