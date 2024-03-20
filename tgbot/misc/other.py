def formatted(value, decimal=0):
    try:
        value = float(value)

        if value.is_integer():
            return f'{round(value):,}'.replace(',', ' ')

        if decimal > 0:
            return f'{round(value, decimal):,}'.replace(',', ' ')

        return f'{round(value):,}'.replace(',', ' ')
    except:
        return value
