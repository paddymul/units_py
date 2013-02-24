import unittest

class InvalidType(Exception):
    pass

class InvalidExpressionException(Exception):
    pass


class BaseDimension(object):
    """ this class needs to be overridden with the unit_system
    attribute set """
    def __init__(self, dimension_name, unit_system):
        self.__name__ = dimension_name
        self.unit_system = unit_system

    def __repr__(self):
        return self.__name__

    def __mul__(self, other):
        sc, oc = self.__class__, other.__class__
        if not oc == sc:
            InvalidExpressionException(
                "No way to multiply classes of type %r and %r" % (sc, oc))
        return "%s*%s" % (self.__name__, other.__name__)

    def _div__(self, other):
        sc, oc = self.__class__, other.__class__
        if not oc == sc:
            InvalidExpressionException(
                "No way to divided classes of type %r and %r" % (sc, oc))
        return "%s/%s" % (self.__name__, other.__name__)



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
    for expression, result_type in new_relations:

        table[expression] = result_type
    return table

def traverse_no_cycle(starting_unit, found_units=None):
    if not found_units:
        found_units = []
    found_units.append(starting_unit)
    if not starting_unit.conversion:
        return found_units

    for unit, conv_factor in starting_unit.conversion:
        if unit in found_units:
            continue
        found_units.extend(traverse_no_cycle(unit, found_units))
    return found_units


def directly_reachable(from_unit, to_unit):
    for unit_, conv_factor in from_unit.conversion:
        if to_unit == unit_:
            return True
    return False

def make_bidirectional(starting_unit):
    if not starting_unit.conversion:
        return
    for unit_, conv_factor in starting_unit.conversion:
        if directly_reachable(unit_, starting_unit):
            # if there is already a conversion factor, don't put
            # another one in
            continue
        unit_.conversion.append(
            [starting_unit, (1.0 / conv_factor)])

def make_list_bidirectional(unit_list):
    map(make_bidirectional, unit_list)

def verify_same_type(unit_list):
    if len(unit_list) < 2:
        return True
    base_unit = unit_list[0]
    base_dim = base_unit.dimension
    for unit_ in unit_list:
        if not unit_.dimension == base_dim:
            raise NoConversionPossible(
                "Cannot convert from %r of %r to %r of %r " %\
                    (base_unit, base_dim, unit_, unit_.dimension))
    return True

def verify_reachability(unit_list):
    found_units = []
    if len(unit_list) < 2:
        #all elements are reachable when there are 0 or 1 elements
        return True
    starting_unit = False

    for unit_ in unit_list:
        if not unit_.conversion:
            continue
        else:
            # pick the first unit with a conversion fractor
            starting_unit = unit_
            break
    if not starting_unit:
        #if there are multiple units and not of them had a conversion
        #factor, there is no way to traverse all of them
        raise UnreachableUnit(
            "none of the units have conversion, each is their own island" +\
                unit_list)
    all_tree_memebers = traverse_no_cycle(starting_unit)
    unreachable_units = []
    for unit_ in unit_list:
        if unit_ not in all_tree_memebers:
            unreachable_units.append(unit_)
    if unreachable_units:
        raise UnreachableUnit(
            "all of %r are unreachable starting from %r" %\
                (unreachable_units, starting_unit))
    return True

def verify_unit_dimension_table(udt):
    for type_name, unit_list in udt.items():
        make_list_bidirectional(unit_list)
        verify_reachability(unit_list)
        verify_same_type(unit_list)

def find_path(start, end, working_path=False, tried=False):
    if not working_path:
        working_path = []
    if not tried:
        tried = []
    working_path.append(start)
    tried.append(start)
    if start == end:
        return working_path
    for unit_, conv_factor in start.conversion:
        if unit_ not in tried:
            possible_path = find_path(unit_, end, working_path, tried)
            if possible_path:
                return possible_path
    return False

class UnreachableUnit(Exception):
    pass

class NoConversionPossible(Exception):
    pass


class BaseUnit(object):
    def __init__(self, quantity):
        self.nominal_quantity = quantity
        self.real_quantity = quantity * self.conversion_factor

    conversion_factor = 1
    conversion = False

    def __div__(self, other):
        ot_cl = other.__class__
        sl_cl = self.__class__
        if ot_cl in [float, int]:
            return sl_cl(self.nominal_quantity / other)

        sl_dm = sl_cl.dimension
        ot_dm = ot_cl.dimension
        type_def = "%s/%s" % (ot_dm.__name__, sl_dm.__name__)
        if sl_dm.unit_system.DimensionRelationTable.has_key(type_def):
            new_dimension = sl_dm.unit_system.DimensionRelationTable[type_def]
            new_bu = new_dimension.base_unit
            return new_bu(self.real_quantity / ot.real_quantity)
        else:
            raise InvalidType(
                "No way to multiply %s and %s" % (sl_cl, ot_cl))
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

    def convert_to(self, other_unit):
        correct_conv = False
        for unit_, conv_factor in self.conversion:
            if unit_ == other_unit:
                correct_conv = conv_factor
        if not correct_conv:
            raise NoConversionPossible(
                "no conversion from %r to %r" % (self.__class__, other_unit))
        else:
            return self.dimension(self.quantity * conv_factor, other_unit)


"""
Key insight, you don't add instatiated dimensions, you add units.  Put
another way, you don't add Length and Length, you add 3 feet and 3
feet, or 3 feet and 1 meter

"""
class UnitSystem(object):

    def __init__(self):
        self.DimensionRelationTable = {}
        self.UnitDimensionTable = {}

    def new_dimension(self, dimension_name, base_unit_name):
        if self.DimensionRelationTable.has_key(dimension_name):
            raise AlreadyDefinedException("%s already defined" % dimension_name)
        temp_dim = BaseDimension(dimension_name, self)
        self.DimensionRelationTable[dimension_name] = temp_dim
        class TempUnit(BaseUnit):
            dimension = temp_dim
            conversion = []
        TempUnit.__name__ = base_unit_name
        temp_dim.base_unit = TempUnit
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

# UnitDimensionTable = {
#     "Length" : [Meter],
#     "Time" : [Second, Minute]}


us = UnitSystem()
Meter = us.new_dimension("Length", "Meter")
Second= us.new_dimension("Time", "Second")
#Minute = Second.dimension.add_unit(60 * Second, "Minute")
Length = Meter.dimension
#Area = us.add_derived_dimension(Length * Length, "Area", "Meter^2")


# Meter = Length.unit("M", "Meter")

# class Meter(Unit):
#     dimension = Length

# class Second(Unit):
#     dimension = Time

# class Minute(Unit):
#     dimension = Time
#     conversion = [[Second, 60]]



class TestDimensions(unittest.TestCase):

    def test_fill(self):
        mult_table = {"Length*Length":"Area"}
        n_table = _fill_relational_table(mult_table)
        self.assertEquals(
            len(n_table.keys()), 2)
        self.assertTrue(
            "Area/Length" in n_table.keys())
        self.assertEquals(n_table['Area/Length'], 'Length')

        div_table = {"Length/Time":"Speed"}
        nd_table = _fill_relational_table(div_table)
        self.assertEquals(
            len(nd_table.keys()), 2)
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

'''
us = UnitSystem()
Length = us.new_dimension("Length")
Area = us.add_derived_dimension(Length * Length, "Area")


class Length(Dimension):
    pass

class Area(Dimension):
    pass

class Time(Dimension):
    pass

class Speed(Dimension):
    pass




ConversionTable = {
    "Feet_Meters" : 3.28084
}



class Units(object):
    def __init__(self, dimension, short_name, long_name, in_terms_of=None):
        self.dimension, self.short_name = dimension, short_name
        self.long_name = long_name

        if in_terms_of:
            self.setup_conversion(*in_terms_of)
















class MyMeta(type):
    def __new__(meta, name, bases, dct):
        print '-----------------------------------'
        print "Allocating memory for class", name
        print meta
        print bases
        print dct
        return super(MyMeta, meta).__new__(meta, name, bases, dct)
    def __init__(cls, name, bases, dct):
        print '-----------------------------------'
        print "Initializing class", name
        print cls
        print bases
        print dct
        super(MyMeta, cls).__init__(name, bases, dct)


class MyKlass(object):
    __metaclass__ = MyMeta

    def foo(self, param):
        pass

    barattr = 2


class TestUnits(unittest.TestCase):
    def test_conversion(self):

        class Feet(Unit):
            dimension = Length
            conversion = []
        class Meter(Unit):
             dimension = Length
             conversion = [[Feet, 3.2084]]


        self.assertEquals(
            Meter(1).convert_to(Feet), Length(3.2084))
        make_bidirectional(Meter)

        self.assertEquals(
            Feet(3.2084).convert_to(Meter), Length(1))
    def test_traverse_no_cycle(self):
        class Quark(Unit):
            dimension = Length
            conversion = []
        class QuarkW(Unit):
            dimension = Length
            conversion = [[Quark, 30]]

    def test_make_bidirectional(self):
        class Quark(Unit):
            dimension = Length
            conversion = []
        class QuarkW(Unit):
            dimension = Length
            conversion = [[Quark, 30]]
        self.assertEquals(len(Quark.conversion),0)
        make_bidirectional(QuarkW)
        self.assertEquals(len(Quark.conversion),1)

    def test_reachability(self):
        class Quark(Unit):
            dimension = Length
            conversion = []

        class QuarkW(Unit):
            dimension = Length
            conversion = [[Quark, 30]]

        class QuarkZ(Unit):
            dimension = Length
            conversion = [[QuarkW, 10]]

        class Buzz(Unit):
            dimension = Length
            conversion = []

        class BuzzB(Unit):
            dimension = Length
            conversion = [[Buzz, 25]]

        class Bridge(Unit):
            dimension = Length
            conversion = [[Buzz,34], [Quark, 8]]
        make_list_bidirectional(
            [Quark, QuarkW, QuarkZ, Buzz, BuzzB, Bridge])
        self.assertTrue(verify_reachability([]))
        self.assertTrue(verify_reachability([Quark]))
        self.assertTrue(verify_reachability([Quark, QuarkW]))
        self.assertTrue(verify_reachability([Quark, QuarkW, Buzz, Bridge]))

    def test_reachability2(self):
        """ this needs to be run separetly because
        make_list_bidirectional provides links that aren't necessarily
        in unit_list"""
        class Quark(Unit):
            dimension = Length
            conversion = []
        class Buzz(Unit):
            dimension = Length
            conversion = []
        class QuarkW(Unit):
            dimension = Length
            conversion = [[Quark, 30]]
        class BuzzB(Unit):
            dimension = Length
            conversion = [[Buzz, 25]]
        make_list_bidirectional([QuarkW, Quark, Buzz, BuzzB])
        def unreachable1():
            verify_reachability([Quark, Buzz])
        def unreachable2():
            verify_reachability([QuarkW, BuzzB, Buzz])

        print "="*80
        print find_path(Quark, Buzz)
        print "="*80
        self.assertRaises(UnreachableUnit, unreachable1)
        self.assertRaises(UnreachableUnit, unreachable2)


    def test_same_type(self):
        class Quark(Unit):
            dimension = Length
        class QuarkW(Unit):
            dimension = Length
        class QuarkZ(Unit):
            dimension = Time
        self.assertTrue(verify_same_type([]))
        self.assertTrue(verify_same_type([Quark]))
        self.assertTrue(verify_same_type([Quark, QuarkW]))
        def incompatible():
            verify_same_type([Quark, QuarkZ])
        self.assertRaises(NoConversionPossible, incompatible)


'''
