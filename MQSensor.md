1 - To convert ppm or ppb to µg/m³ in 1 atm and 25°C (used in code)

    The equation to convert ppm to µg/m³ for a Z ppm concentration of a given element/compost is:

    C = 40.9 * Z * molecular_weight (µg/m³) 

    for a M ppb concentration:

    C = 0.0409 * M * molecular_weight (µg/m³)

    where:
    C: is the equivalent ppm value in µg/m³.
    Z: is the ppm concentration of a given 
    element/compost.
    M: is the ppb concentration of a given 
    element/compost.
    molecular_weight: is the molecular weight of the element/compost in gram/mole.  
    
2 - To convert ppm or ppb to µg/m³ in some known pressure (X in atm) and temperature (Y in Kelvin)

    The equation to convert ppm to µg/m³ for a Z ppm concentration of a given element/compost is:

    C = 12.195 * Z * (X/Y) * molecular_weight (µg/m³) 

    for a M ppb concentration:

    C = 0.012195 * M * (X/Y) * molecular_weight (µg/m³)

    where:
    C: is the equivalent ppm value in µg/m³.
    Z: is the ppm concentration of a given 
    element/compost.
    M: is the ppb concentration of a given 
    element/compost.
    molecular_weight: is the molecular weight of the element/compost in gram/mole.
    X: is the current atmosphere pressure in atm.
    Y: is the current temperature value in Kelvin.



## Links:
- [Controle da poluição atmosférica, Cap 1, page 16](http://www.fap.if.usp.br/~hbarbosa/uploads/Teaching/FisPoluicaoAr2016/Lisboa_Cap1_Introducao_2007.pdf)