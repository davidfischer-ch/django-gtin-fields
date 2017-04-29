""" Provides validation for common GTIN fields.

Available fields:

    ISBNValidator (ISBN)
    UPCAValidator (UPC-A / GTIN-12)
    EANValidator (EAN-13 / GTIN-13)
    GTIN14Validator (GTIN-14)
    ASINValidator (Amazon Standard Identification Number, possible values)
    ASINStrictValidator (Amazon Standard Identification Number, currently known values)
"""
import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy
from gtin_fields import gtin
from stdnum import isbn


class ProductCodeValidatorBase:
    """ A generic product code validator.

    Expects the following attributes on self:

        verbose_object_name (str): The human readable name of the thing being validated).
        valid_lengths (anything that __contains__): The lengths that are valid.
    """
    chartype_message = "Only alpha-numeric characters allowed."
    verbose_object_name = "Product Code"

    def validate(self, value):
        """ Validates the given value. """
        self.validate_type(value)
        self.validate_length(value)
        self.validate_character_types(value)

    def validate_type(self, value):
        if not isinstance(value, str):
            self.invalid("Not a string")

    def validate_length(self, value):
        if len(value) not in self.valid_lengths:
            self.invalid("Wrong length")

    def validate_character_types(self, value):
        if not value.alnum():
            self.invalid(self.chartype_message)

    def error_msg(self, problem_description):
        return "Invalid {}: {}".format(self.verbose_object_name, problem_description)

    def invalid(self, problem_description):
        raise ValidationError(ugettext_lazy(self.error_msg(problem_description)))


class _ASINValidator(ProductCodeValidatorBase):
    # valid as of 2017, see http://stackoverflow.com/a/12827734/422075
    strict_regex = re.compile(r'^B[\dA-Z]{9}|\d{9}(X|\d)$')
    strict_chartype_message = "Must start with 'B' and be alphanumeric, or all digits, or all digits with terminal 'X'"

    def strict_valid_char_types(self, value):
        if not self.strict_regex.match(value):
            self.invalid(self.strict_chartype_message)

    def __init__(self, *args, **kwargs):
        if kwargs.pop('strict', None):
            self.validate_character_types = self.strict_valid_char_types

        super().__init__(*args, **kwargs)


class GTINValidatorBase(ProductCodeValidatorBase):
    """ Validation base for common GTIN codes.

    Expects the following attributes on self:

        verbose_object_name (str): The human readable name of the thing being validated).
        valid_lengths (anything that __contains__): The lengths that are valid.
        is_valid_checksum (callable): A static function returning a bool if
            given correct checksum.  Note: to prevent the function from being
            bound to the class you will need to wrap the function with
            staticmethod()!!
    """
    chartype_message = "Only numbers allowed."

    def validate(self, value):
        """ Validates the given value. """
        super().validate(value)
        self.valid_checksum(value)

    def validate_character_types(self, value):
        if not value.isdigit():
            self.invalid(self.chartype_message)

    def valid_checksum(self, value):
        if not self.is_valid_checksum(value):
            self.invalid('Failed checksum')


class _ISBNValidator(GTINValidatorBase):
    """ Check string is a well-formed ISBN number"""
    verbose_object_name = "ISBN"
    valid_lengths = (10, 13)
    is_valid_checksum = staticmethod(isbn.is_valid)


class _UPCAValidator(GTINValidatorBase):
    """ Check string is a well-formed GTIN-12 / UPC-A code. """
    verbose_object_name = "UPC-A"
    valid_lengths = (12,)
    is_valid_checksum = staticmethod(gtin.is_valid)


class _EAN13Validator(GTINValidatorBase):
    """ Check string is a well-formed GTIN-13 / EAN-13 code. """
    verbose_object_name = "EAN-13"
    valid_lengths = (13,)
    is_valid_checksum = staticmethod(gtin.is_valid)


class _GTIN14Validator(GTINValidatorBase):
    """ Check string is a well-formed GTIN-14 code. """
    verbose_object_name = "GTIN-14"
    valid_lengths = (14,)
    is_valid_checksum = staticmethod(gtin.is_valid)



ISBNValidator = _ISBNValidator().validate
UPCAValidator = _UPCAValidator().validate
EAN13Validator = _EAN13Validator().validate
GTIN14Validator = _GTIN14Validator().validate
ASINValidator = _ASINValidator().validate
ASINStrictValidator = _ASINValidator(strict=True).validate
