from simple_units.base import  UnitSystem

us = UnitSystem()

def n_dim(dim_name, base_unit_name):
    base_unit = us.new_dimension(dim_name, base_unit_name)
    dim = base_unit.dimension
    return (base_unit, dim)

def d_dim(dimension_expression, dim_name, base_unit_name):
    base_unit = us.add_derived_dimension(
        dimension_expression, dim_name, base_unit_name)
    dim = base_unit.dimension
    return (base_unit, dim)


Meter, Length = n_dim("Length", "Meter")
Kilogram, Mass = n_dim("Mass", "Kilogram")
Second, Time= n_dim("Time", "Second")
Ampere, Electric_Current = n_dim("Electric_Current", "Ampere")
Kelvin, Temperature = n_dim("Temperature", "Kelvin")
Candela, Luminous_Intensity = n_dim("Luminous_Intensity", "Candela")
Mole, Amount_of_Substance = n_dim("Amount_of_Substance", "Mole")

Meter_2 = us.add_derived_dimension(Length * Length, "Area", "Meter^2")
Area = Meter_2.dimension
Meter_3 = us.add_derived_dimension(Area * Length, "Volume", "Meter^3")

#cannot define hertz

Meters_Second = us.add_derived_dimension(
    Length / Time, "Velocity", "Meters_second")
Velocity = Meters_Second.dimension

#Acceleration_unit = us.add_derived_dimension(
#    Velocity
