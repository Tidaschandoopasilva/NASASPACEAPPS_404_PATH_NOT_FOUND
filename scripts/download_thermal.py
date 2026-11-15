"""Cache the Mars Odyssey THEMIS daytime infrared mosaic over the Jezero ROI."""
import download_data as trek

if __name__ == '__main__':
    layer = 'THEMIS_DayIR_ControlledMosaics_100m_v2_oct2018'
    trek.CAP = f'https://trek.nasa.gov/tiles/Mars/EQ/{layer}/1.0.0/WMTSCapabilities.xml'
    trek.main('themis-context', '9')
