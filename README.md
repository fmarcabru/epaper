# epaper



## To work with fonts:
* Get a font from a website like https://www.fontsquirrel.com/
* load it in Fontforge and select the glyphs required
  From the element menu, select Bitmap Strikes Available and set the size.
  From the file menu, select generate fonts
  select No Outline Font and BDF
  more info below
  https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display/conversion
* Use font_to_font.py to convert the exported font to a python file 
  font-to-py.py sourcefont.bdf size outfount.py
  https://github.com/peterhinch/micropython-font-to-py
  