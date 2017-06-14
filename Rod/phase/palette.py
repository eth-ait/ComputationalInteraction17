def load_gimp_palette(fname):
    f = open(fname, 'r')
    
    colors = []
    for line in f:
        
        try:
            r = int(line[0:4])
            g = int(line[4:8])
            b = int(line[8:12])
            colors.append((r/255.0, g/255.0, b/255.0))
        except:
            pass
    f.close()
    
    return colors
    
        
    