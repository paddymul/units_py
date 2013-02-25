import pdb
import unittest

class InvalidType(Exception):
    pass

class InvalidExpressionException(Exception):
    pass

class UnitExpression(object):
    def __init__(self, conversion_factor, dimension):
        self.conversion_factor = conversion_factor
        self.dimension = dimension

class ExprMetaclass(type):

    def __mul__(self, other):
        ot_cl = other.__class__
        sl_cl = self

        if ot_cl in [float, int]:
            return UnitExpression(
                sl_cl.conversion_factor * other,
                sl_cl.dimension)
        else:
            raise InvalidExpressionException(
                "currently only multiplication by primitives is supported")

    __rmul__ = __mul__

    def __div__(self, other):
        ot_cl = other.__class__
        sl_cl = self

        if ot_cl in [float, int]:
            return UnitExpression(
                sl_cl.conversion_factor / other,
                sl_cl.dimension)
        else:
            raise InvalidExpressionException(
                "currently only division by primitives is supported")


class BaseDimension(object):
    """ this class needs to be overridden with the unit_system
    attribute set """
    def __init__(self, dimension_name, unit_system):
        self.__name__ = dimension_name
        self.unit_system = unit_system

    def __repr__(self):
        return self.__name__

    def __mul__(self, other):
        return "%s*%s" % (self.__name__, other.__name__)

    def _div__(self, other):
        return "%s/%s" % (self.__name__, other.__name__)
    Units = []


class AlreadyDefinedException(Exception):
    pass

def _fill_relational_table(table):
    new_relations = []
    for expression, resultant_type in table.items():
        mult_components = expression.split("*")
        if len(mult_components) > 1:
            left_type, right_type = mult_components
            new_relations.append(
                ["%s*%s" % (right_type, left_type), resultant_type])
            new_relations.append(
                ["%s/%s" % (resultant_type, left_type), right_type])
            new_relations.append(
                ["%s/%s" % (resultant_type, right_type), left_type])
        div_components = expression.split("/")
        if len(div_components) > 1:
            left_type, right_type = div_components
            new_relations.append(
                ["%s*%s" % (resultant_type, right_type), left_type])
    for expression, result_type_name in new_relations:
        #result_type = table[result_type_name]
        if type(result_type_name) == type("a"):
            result_type = table[result_type_name]
        else:
            result_type = result_type_name
        table[expression] = result_type
    return table

class NoConversionPossible(Exception):
    pass

class BaseUnit(object):
    def __init__(self, quantity, base_quantity=False):
        self.nominal_quantity = quantity
        self.real_quantity = quantity * self.conversion_factor
        if base_quantity:
            self.real_quantity = base_quantity
            self.nominal_quantity = base_quantity / self.conversion_factor

    conversion_factor = 1.0
    conversion = False

    __metaclass__ = ExprMetaclass

    def __div__(self, other):
        ot_cl = other.__class__
        sl_cl = self.__class__
        if ot_cl in [float, int]:
            return sl_cl(self.nominal_quantity / other)

        sl_dm = sl_cl.dimension
        ot_dm = ot_cl.dimension
        type_def = "%s/%s" % (sl_dm.__name__, ot_dm.__name__)
        if sl_dm.unit_system.DimensionRelationTable.has_key(type_def):
            new_dimension = sl_dm.unit_system.DimensionRelationTable[type_def]
            new_bu = new_dimension.base_unit


            return new_bu(self.real_quantity / other.real_quantity)
        else:
            raise InvalidType(
                "No way to divide %s and %s" % (sl_cl, ot_cl))

    def __mul__(self, other):
        ot_cl = other.__class__
        sl_cl = self.__class__
        if ot_cl in [float, int]:
            return sl_cl(self.nominal_quantity * other)

        sl_dm = sl_cl.dimension
        ot_dm = ot_cl.dimension
        type_def = "%s*%s" % (ot_dm.__name__, sl_dm.__name__)
        if sl_dm.unit_system.DimensionRelationTable.has_key(type_def):
            new_dimension = sl_dm.unit_system.DimensionRelationTable[type_def]
            new_bu = new_dimension.base_unit
            return new_bu(self.real_quantity * other.real_quantity)
        else:
            raise InvalidType(
                "No way to multiply %s and %s" % (sl_cl, ot_cl))
    __rdiv__ = __div__
    __rmul__ = __mul__

    def __add__(self, other):
        ot_cl = other.__class__
        sl_cl = self.__class__

        sl_dm = sl_cl.dimension
        ot_dm = ot_cl.dimension

        if sl_dm == ot_dm:
            return sl_dm.base_unit(self.real_quantity + other.real_quantity)
        else:
            raise InvalidType(
                "No way to add %s to %s" % (sl_cl, ot_cl))

    def __sub__(self, other):
        ot_cl = other.__class__
        sl_cl = self.__class__

        sl_dm = sl_cl.dimension
        ot_dm = ot_cl.dimension

        if sl_dm == ot_dm:
            return sl_dm.base_unit(self.real_quantity - other.real_quantity)
        else:
            raise InvalidType(
                "No way to subtract %s from %s" % (ot_cl, sl_cl))

    def __eq__(self, other):
        ot_cl = other.__class__
        sl_cl = self.__class__

        sl_dm = sl_cl.dimension
        ot_dm = ot_cl.dimension

        if sl_dm == ot_dm:
            return self.real_quantity == other.real_quantity
        else:
            raise InvalidType(
                "No way to compare %s to %s" % (ot_cl, sl_cl))

    def __abs__(self):
        sl_cl = self.__class__
        return sl_cl(abs(self.nominal_quantity*1.0))

    def __round__(self):
        sl_cl = self.__class__
        return sl_cl(round(self.nominal_quantity*1.0))

    def convert_to(self, other_unit_kls):
        ot_cl = other_unit_kls
        sl_cl = self.__class__

        if not ot_cl in self.dimension.Units:
            raise NoConversionPossible(
                "no conversion from %r to %r" % (sl_cl, ot_cl))
        else:
            return ot_cl(0, self.real_quantity)

    def __str__(self):
        return "%r %s" % (self.nominal_quantity, self.__name__)

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
"""
Key insight, you don't add instatiated dimensions, you add units.  Put
another way, you don't add Length and Length, you add 3 feet and 3
feet, or 3 feet and 1 meter

"""
class UnitSystem(object):

    def __init__(self):
        self.DimensionRelationTable = {}
        self.UnitDimensionTable = {}
        self.Dimensions = AttributeDict()
        self.Units = AttributeDict()

    def new_dimension(self, dimension_name, base_unit_name):
        if self.DimensionRelationTable.has_key(dimension_name):
            raise AlreadyDefinedException("%s already defined" % dimension_name)
        temp_dim = BaseDimension(dimension_name, self)
        self.DimensionRelationTable[dimension_name] = temp_dim
        class TempUnit(BaseUnit):
            dimension = temp_dim
            __name__ = base_unit_name
        temp_dim.base_unit = TempUnit
        temp_dim.Units.append(TempUnit)
        self.Dimensions[dimension_name] = temp_dim
        self.Units[base_unit_name] = TempUnit
        self.UnitDimensionTable[dimension_name] = [TempUnit]
        return TempUnit

    def add_derived_dimension(self, derived_def,
                              dimension_name, derived_unit_name):
        if self.DimensionRelationTable.has_key(derived_def):
            raise AlreadyDefinedException("%s already defined" % derived_def)
        derived_unit_kls = self.new_dimension(dimension_name, derived_unit_name)
        self.DimensionRelationTable[derived_def] = derived_unit_kls.dimension
        self._fill_relational_table()
        return derived_unit_kls

    def _fill_relational_table(self):
        drt = self.DimensionRelationTable
        self.DimensionRelationTable = _fill_relational_table(drt)

    def add_unit(self, new_unit_name, unit_expression):
        class TempUnit(BaseUnit):
            dimension = unit_expression.dimension
            conversion_factor = unit_expression.conversion_factor
            __name__ = new_unit_name
        TempUnit.dimension.Units.append(TempUnit)
        self.Units[new_unit_name] = TempUnit

        return TempUnit


# UnitDimensionTable = {
#     "Length" : [Meter],
#     "Time" : [Second, Minute]}


us = UnitSystem()
Meter = us.new_dimension("Length", "Meter")
Second= us.new_dimension("Time", "Second")
#Minute = Second.dimension.add_unit(60 * Second, "Minute")
Length = Meter.dimension
Meter_2 = us.add_derived_dimension(Length * Length, "Area", "Meter^2")

print Meter(1)
print Meter_2(1)
Feet = us.add_unit("Feet", Meter / 3.208)
print Meter(1), Meter(1).convert_to(Feet)
class TestUnits(unittest.TestCase):


    def test_conversion(self):
        us = UnitSystem()
        Meter = us.new_dimension("Length", "Meter")
        Feet = us.add_unit("Feet", Meter / 3.208)
        Yard = us.add_unit("Yard", Feet * 3)

        f, m = Feet(3.208), Meter(1)
        print f.real_quantity, m.real_quantity
        self.assertAlmostEqual(f.real_quantity,m.real_quantity)
        self.assertUnitAlmostEqual(f,m)
        self.assertAlmostEqual(Feet(3), Yard(1))
        self.assertAlmostEqual(Feet(3), Feet(1) * 3)
        self.assertAlmostEqual(Feet(3), 3 * Feet(1))
        self.assertAlmostEqual(Feet(1),  Feet(3) / 3)
        self.assertAlmostEqual(Feet(1),  Feet(3) / 3)

    def test_convert_to(self):
        us = UnitSystem()
        Meter = us.new_dimension("Length", "Meter")
        Feet = us.add_unit("Feet", Meter / 3.208)
        Yard = us.add_unit("Yard", Feet * 3)

        self.assertUnitAlmostEqual(Feet(1), Feet(1).convert_to(Meter))

        self.assertAlmostEqual(Feet(3), Yard(1))
        self.assertAlmostEqual(Feet(3), Feet(1) * 3)
        self.assertAlmostEqual(Feet(3), 3 * Feet(1))
        self.assertAlmostEqual(Feet(1),  Feet(3) / 3)
        self.assertAlmostEqual(Feet(1),  Feet(3) / 3)

    def test_derived_dimension_unit(self):
        us = UnitSystem()
        Meter = us.new_dimension("Length", "Meter")
        Second = us.new_dimension("Time", "Second")

        Length = us.Dimensions.Length
        Msq = us.add_derived_dimension(Length * Length, "Area", "Meter^2")

        self.assertAlmostEqual(
            Meter(10), (Msq(100) / Meter(10)))

        Area = us.Dimensions.Area
        Mcb = us.add_derived_dimension(Area * Length, "Volume", "Meter^3")

        self.assertAlmostEqual(
            Msq(100), Mcb(1000)/(Meter(10)))

    def assertUnitAlmostEqual(self, first, second,
                          places=None, msg=None, delta=None):
        """Fail if the two objects are unequal as determined by their
           difference rounded to the given number of decimal places
           (default 7) and comparing to zero, or by comparing that the
           between the two objects is more than the given delta.

           Note that decimal places (from zero) are usually not the same
           as significant digits (measured from the most signficant digit).

           If the two objects compare equal then they will automatically
           compare almost equal.
        """
        if first == second:
            # shortcut
            return
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")

        if delta is not None:
            if abs(first - second) <= delta:
                return

            standardMsg = '%s != %s within %s delta' % (safe_repr(first),
                                                        safe_repr(second),
                                                        safe_repr(delta))
        else:
            if places is None:
                places = 7

            abs_ = abs(second.real_quantity - first.real_quantity)
            if round(abs_, places) == 0:
                return

            standardMsg = '%s != %s within %r places' % (safe_repr(first),
                                                          safe_repr(second),
                                                          places)
        msg = self._formatMessage(msg, standardMsg)
        raise self.failureException(msg)

class TestDimensions(unittest.TestCase):

    def test_fill(self):
        mult_table = {"Length*Length":"Area", "Area":"Area", "Length":"Length"}
        n_table = _fill_relational_table(mult_table)
        self.assertEquals(len(n_table.keys()), 4)
        self.assertTrue(
            "Area/Length" in n_table.keys())
        self.assertEquals(n_table['Area/Length'], 'Length')

        div_table = {"Length/Time":"Speed", "Length":"Length",
                     "Time":"Time", "Speed":"Speed"}
        nd_table = _fill_relational_table(div_table)
        self.assertEquals(
            len(nd_table.keys()), 5)
        self.assertTrue(
            "Speed*Time" in nd_table.keys())
        self.assertEquals(nd_table['Speed*Time'], 'Length')


    def test_instatiation(self):
        class LLength(BaseDimension):
            us = UnitSystem()
            Meter = us.new_dimension("Length", "Meter",)
            Meter(10)

    def test_equality(self):
        us = UnitSystem()
        Meter = us.new_dimension("Length", "Meter",)
        self.assertEquals(
            Meter(10), Meter(10))
    def test_like_addition(self):
        us = UnitSystem()
        LLength = us.new_dimension("LLength", "Meter")
        expected20 = LLength(10) + LLength(10)
        self.assertEquals(expected20, LLength(20))
    def test_unlike_addition(self):
        us = UnitSystem()
        LLength = us.new_dimension("LLength", "Meter")
        LTime = us.new_dimension("LTime", "Second")
        def unlike():
            no_answer = LLength(10) + LTime(20)
        self.assertRaises(InvalidType, unlike)

    def test_multiply(self):
        us = UnitSystem()
        Meter = us.new_dimension("Length", "Meter",)
        Length = Meter.dimension
        Msq = us.add_derived_dimension(Length * Length, "Area", "Meter^2")
        self.assertEquals(
            Meter(10) * Meter(10), Msq(100))

if __name__ == "__main__":
    unittest.main()
