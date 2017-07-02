from bika.lims import _
from plone.supermodel import model
from plone import api
from zope import schema
from datetime import date
from Products.CMFCore.permissions import ModifyPortalContent, AddPortalContent
from plone.dexterity.content import Container
from zope.interface import implements

from plone.namedfile.field import NamedBlobFile

class IContract(model.Schema):

        title = schema.TextLine(
                title=_(u"title"),
                description=_(u""),
                required=True
                )

        company_client = schema.Text(
                title=_(u"societe client"),
                description=_(u""),
                required=False
                )

	representant_client= schema.Text(
                title=_(u"representant du client"),
                description=_(u""),
                required=False
                )

	representant_center = schema.Text(
                title=_(u"representant du centre"),
                description=_(u""),
                required=False
                )
	doc = NamedBlobFile(
                title=_(u"documentation"),
                description=_(u""),
                required=True
                )

class Contract(Container):
    
    implements(IContract)
    
    
