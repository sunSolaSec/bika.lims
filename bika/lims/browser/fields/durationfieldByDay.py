# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.ATExtensions.ateapi import RecordField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t


class DurationFieldByDay(RecordField):

    """ Stores duration in Years/Months/Days """
    security = ClassSecurityInfo()
    _properties = RecordField._properties.copy()
    _properties.update({
        'type': 'duration',
        'subfields': ('years', 'months', 'days'),
        'subfield_labels': {'years': _('Years'),
                            'months': _('Months'),
                            'days': _('Days')},
        'subfield_sizes': {'years': 2,
                           'months': 2,
                           'days': 2},
        'subfield_validators': {'years': 'duration_validator',
                                'months': 'duration_validator',
                                'days': 'duration_validator'},
    })

registerField(DurationField,
              title="Duration",
              description="Used for storing durations",
              )
