import unittest

class InvalidType(Exception):
    pass

DimensionRelationTable = {
    "Length*Length":"Area",
    "Length/Time": "Speed"}

class Dimension(object):
    def __mul__(self, multiplicant):
        mp_cl = multiplicant.__class__
        sl_cl = self.__class__
        if mp_cl in [float, int]:
            return sl_cl(self.quantity * multiplicant)

        type_def = "%s*%s" % (mp_cl.__name__, sl_cl.__name__)
        if DimensionRelationTable.has_key(type_def):
            r_type = TypeTable[DimensionRelationTable[type_def]]
            return r_type(self.quantity * multiplicant.quantity)
        else:
            raise InvalidType(
                "No way to multiply %s and %s" % (sl_cl, mp_cl))

    def __div__(self, denominator):
        dn_cl = dividen.__class__
        sl_cl = self.__class__
        if dn_cl in [float, int]:
            return sl_cl(self.quantity / denominator)

        type_def = "%s/%s" % (sl_cl.__name__, dn_cl.__name__)
        if DimensionRelationTable.has_key(type_def):
            r_type = TypeTable[DimensionRelationTable[type_def]]
            return r_type(self.quantity / denominator.quantity)
        else:
            raise InvalidType(
                "No way to divide %s by %s" % (sl_cl, dn_cl))

    def __init__(self, quantity):
        self.quantity = quantity

    def __add__(self, addend):
        ad_cl = addend.__class__
        sl_cl = self.__class__
        if ad_cl == sl_cl:
            return sl_cl(self.quantity + addend.quantity)
        else:
            raise InvalidType(
                "No way to add %s to %s" % (sl_cl, ad_cl))

    def __sub__(self, subtend):
        sb_cl = subtend.__class__
        sl_cl = self.__class__
        if sb_cl == sl_cl:
            return sl_cl(self.quantity - subtend.quantity)
        else:
            raise InvalidType(
                "No way to subtract %s from %s" % (sb_cl, sl_cl))

    def __eq__(self, other_side):
        if not other_side.__class__ == self.__class__:
            return False
        if other_side.quantity == self.quantity:
            return True
        return False

    def __repr__(self):
        return "%s %d" % (self.__class__, self.quantity)


def fill_relational_table(table):
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

class Length(Dimension):
    pass

class Area(Dimension):
    pass

class Time(Dimension):
    pass

class Speed(Dimension):
    pass


TypeTable = {
    "Length": Length,
    "Time": Time,
    "Speed": Speed,
    "Area": Area}




class TestDimensions(unittest.TestCase):

    def test_fill(self):
        mult_table = {"Length*Length":"Area"}
        n_table = fill_relational_table(mult_table)
        self.assertEquals(
            len(n_table.keys()), 2)
        self.assertTrue(
            "Area/Length" in n_table.keys())
        self.assertEquals(n_table['Area/Length'], 'Length')

        div_table = {"Length/Time":"Speed"}
        nd_table = fill_relational_table(div_table)
        self.assertEquals(
            len(nd_table.keys()), 2)
        self.assertTrue(
            "Speed*Time" in nd_table.keys())
        self.assertEquals(nd_table['Speed*Time'], 'Length')


    def test_instatiation(self):
        print Length(10)
    def test_equality(self):
        self.assertEquals(
            Length(10), Length(10))
    def test_like_addition(self):
        expected20 = Length(10) + Length(10)
        self.assertEquals(expected20, Length(20))
    def test_unlike_addition(self):
        def unlike():
            no_answer = Length(10) + Time(20)
        self.assertRaises(InvalidType, unlike)

    def test_multiply(self):
        self.assertEquals(
            Length(10) * Length(10), Area(100))

if __name__ == "__main__":
    unittest.main()
