import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.schema import get_spec_for_prop
from bravado_core.spec import Spec


@pytest.fixture
def address_spec():
    return {
        'type': 'object',
        'properties': {
            'number': {
                'type': 'number'
            },
            'street_name': {
                'type': 'string'
            },
            'street_type': {
                'type': 'string',
                'enum': [
                    'Street',
                    'Avenue',
                    'Boulevard']
            }
        }
    }


@pytest.fixture
def address():
    return {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue'
    }


def test_declared_property(minimal_swagger_spec, address_spec, address):
    expected_spec = address_spec['properties']['street_name']
    result = get_spec_for_prop(
        minimal_swagger_spec, address_spec, address, 'street_name')
    assert expected_spec == result


def test_properties_and_additionalProperties_not_present(minimal_swagger_spec,
                                                         address):
    object_spec = {'type': 'object'}
    result = get_spec_for_prop(
        minimal_swagger_spec, object_spec, address, 'street_name')
    assert result is None


def test_properties_not_present_and_additionalProperties_True(
        minimal_swagger_spec, address):
    object_spec = {
        'type': 'object',
        'additionalProperties': True
    }
    result = get_spec_for_prop(
        minimal_swagger_spec, object_spec, address, 'street_name')
    assert result is None


def test_properties_not_present_and_additionalProperties_False(
        minimal_swagger_spec, address):
    object_spec = {
        'type': 'object',
        'additionalProperties': False
    }
    result = get_spec_for_prop(
        minimal_swagger_spec, object_spec, address, 'street_name')
    assert result is None


def test_additionalProperties_with_spec(minimal_swagger_spec, address_spec,
                                        address):
    address_spec['additionalProperties'] = {'type': 'string'}
    expected_spec = {'type': 'string'}
    # 'city' is not a declared property so it gets classified under
    # additionalProperties
    result = get_spec_for_prop(
        minimal_swagger_spec, address_spec, address, 'city')
    assert expected_spec == result


def test_additionalProperties_not_dict_like(minimal_swagger_spec, address_spec,
                                            address):
    address_spec['additionalProperties'] = 'i am not a dict'
    with pytest.raises(SwaggerMappingError) as excinfo:
        get_spec_for_prop(minimal_swagger_spec, address_spec, address, 'city')
    assert "Don't know what to do" in str(excinfo.value)


def test_object_is_ref(minimal_swagger_dict, address_spec, address):
    minimal_swagger_dict['definitions']['Address'] = address_spec
    address_ref_spec = {'$ref': '#/definitions/Address'}
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    result = get_spec_for_prop(
        swagger_spec, address_ref_spec, address, 'street_type')
    assert  address_spec['properties']['street_type'] == result


def test_properties_is_ref(minimal_swagger_dict, address):
    street_type_spec = {
        'type': 'string',
        'enum': ['Street', 'Avenue', 'Boulevard']
    }

    address_properties_spec = {
        'street_type': street_type_spec
    }

    address_spec = {
        'type': 'object',
        'properties': {
            '$ref': '#/definitions/AddressProperties'
        }
    }

    minimal_swagger_dict['definitions']['AddressProperties'] = \
        address_properties_spec
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    result = get_spec_for_prop(
        swagger_spec, address_spec, address, 'street_type')
    assert  street_type_spec == result


def test_property_is_ref(minimal_swagger_dict, address):
    street_type_spec = {
        'type': 'string',
        'enum': ['Street', 'Avenue', 'Boulevard']
    }

    address_spec = {
        'type': 'object',
        'properties': {
            'street_type': {
                '$ref': '#/definitions/StreetType'
            }
        }
    }

    minimal_swagger_dict['definitions']['StreetType'] = street_type_spec
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    result = get_spec_for_prop(
        swagger_spec, address_spec, address, 'street_type')
    assert  {'$ref': '#/definitions/StreetType'} == result
