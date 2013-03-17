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

def d_dim(base_unit_name, **kwargs):
    assert len(kwargs.values())
    dim_name, dimension_expression = kwargs.items()[0]

    base_unit = us.add_derived_dimension(
        dimension_expression, dim_name, base_unit_name)
    dim = base_unit.dimension
    return (base_unit, dim)


Meter, Length = n_dim("Length", "Meter")
Kilogram, Mass = n_dim("Mass", "Kilogram")
Second, Time= n_dim("Time", "Second")
Ampere, ElectricCurrent = n_dim("ElectricCurrent", "Ampere")
Kelvin, Temperature = n_dim("Temperature", "Kelvin")
Candela, LuminousIntensity = n_dim("LuminousIntensity", "Candela")
Mole, AmountOfSubstance = n_dim("AmountOfSubstance", "Mole")

Meter_2, Area = d_dim("Meter^2", Area = Length * Length)
Meter_3, Volume = d_dim("Meter^3", Volume = Area * Length)

#cannot define hertz with current BaseDimiension class
#Hertz, Frequency = d_dim(1 / time, "Frequency", "Hertz")

MetersSecond, Velocity = d_dim("MetersSecond", Velocity = Length / Time)

AccelerationUnit, Acceleration = d_dim(
    "AccelerationUnit", Acceleration = Velocity / Time)

Newton, Force = d_dim("Newton", Force = Mass * Acceleration)

Velocity_sq_unit, Velocity2 = d_dim(
    "Velocity_sq_unit", Velocity2 = Velocity * Velocity)
Joule, Energy = d_dim("Joule", Energy = Mass * Velocity2)

Watt, Power = d_dim("Watt", Power = Energy / Time)
Pascal, Pressure = d_dim("Pascal", Pressure = Force / Area)
Radian, Angle = d_dim("Radian", Angle = Length / Length)
Streadian, SolidAngle = d_dim("Steradian", SolidAngle = Area / Area)
Columb, ElectricalCharge = d_dim(
    "Columb", ElectricalCharge = ElectricCurrent * Time)
Volt, Voltage = d_dim("Volt", Voltage = Energy * ElectricalCharge)
Farad, Capicitance = d_dim("Farad", Capicitance = ElectricalCharge / Voltage)
Ohm, Resistance = d_dim("Ohm", Resistance = Voltage / ElectricCurrent)
#Siemens, Conductance = d_dim("Siemens", Conductance = 1 / Resistance)
Weber, MagneticFlux = d_dim("Weber", MagneticFlux = Energy / ElectricCurrent)
Tesla, MagneticFieldStrength = d_dim(
    "Tesla", MagneticFieldStrength = MagneticFlux / Area)
#Henry, Inductance = d_dim("Henry", Inductance = MagneticFlux * ElectricCurrent)


Lumen, LuminousFlux = d_dim(
    "Lumen", LuminousFlux = LuminousIntensity * SolidAngle)

Lux, Illuminance = d_dim("Lux", Illuminance = LuminousIntensity / Area)

#Becquerel, Radioactivity = d_dim("Becquerel", Radioactivity = 1 /
#Time)

#Sievert, EquivalentDose = d_dim("Sievert", EquivalentDose = Energy / Mass)
Katal, CatalyticActivity = d_dim(
    "Katal", CatalyticActivity = AmountOfSubstance / Time)
