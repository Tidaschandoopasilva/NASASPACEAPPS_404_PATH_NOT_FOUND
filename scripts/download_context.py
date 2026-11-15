"""Cache additional NASA Mars Trek context over the shared Jezero extent."""
import download_data as trek

for filename, layer, level in [
    ('ctx-context','CTX_beta01_uncontrolled_5m_Caltech','10'),
    ('mola-context','Mars_MOLA_blend200ppx_HRSC_ClrShade_clon0dd_200mpp_lzw','8'),
]:
    trek.CAP = f'https://trek.nasa.gov/tiles/Mars/EQ/{layer}/1.0.0/WMTSCapabilities.xml'
    try:
        trek.main(filename,level)
    except (OSError, ValueError, IndexError) as error:
        print(filename, error)
