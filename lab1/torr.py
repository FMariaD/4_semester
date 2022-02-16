import gmsh
import sys
import numpy as np

gmsh.initialize()

gmsh.model.add("t2")

lc = 1e-2
sl = []

def create_tor(r1, r2, o):
    surfaces = []
    points = [[]]
    vlines = [[]] #вертикальные линии
    hlines = [[]] #горизонтальные линии
    s = 0
    for i in np.arange(0, np.pi*2, o):
        if i!= 0:
            points.append([])
        for j in np.arange(0, np.pi*2, o):
            points[s].append(gmsh.model.geo.addPoint((r1+r2*np.cos(j))*np.cos(i), (r1+r2*np.cos(j))*np.sin(i), r2*np.sin(j)))
        s += 1

    gmsh.model.geo.synchronize()
    
    
    for i in range(0, s):
        if i!= 0:
            hlines.append([])
            vlines.append([])
        k = (i+1) % s
        for j in range(0, len(points[0])):
            q = (j+1) % s
            hlines[i].append(gmsh.model.geo.addLine(points[i][j],points[k][j]))
            vlines[i].append(gmsh.model.geo.addLine(points[i][j],points[i][q]))
            #cl = gmsh.model.geo.addCurveLoop([-l1, l2, l3, l4])
            #surfaces.append(gmsh.model.geo.addPlaneSurface([cl]))
            
    for i in range(0, s):
        k = (i+1) % s
        for j in range(0, len(points[0])):
            q = (j+1) % s
            l1 = hlines[i][j]
            l2 = vlines[k][j]
            l3 = hlines[i][q]
            l4 = vlines[i][j]
            cl = gmsh.model.geo.addCurveLoop([l1, l2, -l3, -l4])
            surfaces.append(gmsh.model.geo.addPlaneSurface([cl]))

    gmsh.model.geo.synchronize()
    sl.append(gmsh.model.geo.addSurfaceLoop([surfaces[i] for i  in range(0, len(surfaces))]))

r1 = 0.5
r2 = 0.2
o1 = np.pi*2 / 18 #interval
o2 = np.pi*2 / 20
create_tor(r1, r2, o1)
create_tor(r1, 3*r2/5, o1)

gmsh.model.geo.addVolume(sl)
gmsh.model.geo.synchronize()

gmsh.option.setNumber("Mesh.MeshSizeFactor", 0.4)
gmsh.option.setNumber("Mesh.ToleranceInitialDelaunay", 1e-12)
gmsh.option.setNumber("Mesh.CharacteristicLengthFromCurvature", 1)
gmsh.option.setNumber("Mesh.ToleranceInitialDelaunay", 1e-12)
gmsh.option.setNumber("Mesh.MinimumElementsPerTwoPi", 10)
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.05)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 0.1)
#gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)

gmsh.model.mesh.generate(3)


gmsh.write("t2.msh")
gmsh.write("t2.geo_unrolled")

if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()
