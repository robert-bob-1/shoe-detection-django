

def get_scraping_strategy_from_url(url):
    """ Get the scraping strategy based on the URL. """
    from .epantofi_strategy import EPantofiScrapingStrategy
    from .officeshoes_strategy import OfficeShoesScrapingStrategy

    if 'epantofi' in url:
        return EPantofiScrapingStrategy()
    elif 'officeshoes' in url:
        return OfficeShoesScrapingStrategy()
    else:
        raise ValueError(f"URL {url} not supported")


def convert_svg_to_binary(logo_svg, width=None, height=None):
    """ Convert SVG image to PNG. """

    from io import BytesIO
    import cairosvg
    from PIL import Image
    out = BytesIO()
    if width == None and height == None:
        cairosvg.svg2png(bytestring=logo_svg.encode('utf-8'), write_to=out)
    else:
        cairosvg.svg2png(bytestring=logo_svg.encode('utf-8'), write_to=out, parent_width=width, parent_height=height)
    out.seek(0)

    with Image.open(out) as image:
        image_buffer = BytesIO()
        image.save(image_buffer, format='PNG')
        return image_buffer.getvalue()
