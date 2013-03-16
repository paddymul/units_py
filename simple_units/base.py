class InvalidType(Exception):
    pass

class InvalidExpressionException(Exception):
    pass

class AlreadyDefinedException(Exception):
    pass

class NoConversionPossible(Exception):
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
        if type(result_type_name) == type("a"):
            result_type = table[result_type_name]
        else:
            result_type = result_type_name
        table[expression] = result_type
    return table

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
        sl_cl = self.__class__ #self klass
        ot_cl = other.__class__ #other klass

        sl_dm = sl_cl.dimension #self dimension
        ot_dm = ot_cl.dimension #other dimension

        if sl_dm == ot_dm:
            return sl_dm.base_unit(self.real_quantity - other.real_quantity)
        else:
            raise InvalidType(
                "No way to subtract %s from %s" % (ot_cl, sl_cl))

    def __eq__(self, other):
        sl_cl = self.__class__ #self klass
        ot_cl = other.__class__ #other klass


        sl_dm = sl_cl.dimension #self dimension
        ot_dm = ot_cl.dimension #other dimension

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
