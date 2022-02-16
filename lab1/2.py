import gmsh
import math
import os
import sys

gmsh.initialize()

def createGeometryAndMesh():
    # Clear all models and merge an STL mesh that we would like to remesh (from
    # the parent directory):
    gmsh.clear()
    #path = os.path.dirname(os.path.abspath(__file__))
    #gmsh.merge(os.path.join(path, os.pardir, 't13_data.stl'))
    gmsh.merge(os.path.join( 'duck.stl'))

    # We first classify ("color") the surfaces by splitting the original surface
    # along sharp geometrical features. This will create new discrete surfaces,
    # curves and points.

    # Angle between two triangles above which an edge is considered as sharp,
    # retrieved from the ONELAB database (see below):
    angle = gmsh.onelab.getNumber('Parameters/Angle for surface detection')[0]

    # For complex geometries, patches can be too complex, too elongated or too
    # large to be parametrized; setting the following option will force the
    # creation of patches that are amenable to reparametrization:
    forceParametrizablePatches = gmsh.onelab.getNumber(
        'Parameters/Create surfaces guaranteed to be parametrizable')[0]

    # For open surfaces include the boundary edges in the classification
    # process:
    includeBoundary = True

    # Force curves to be split on given angle:
    curveAngle = 180

    gmsh.model.mesh.classifySurfaces(angle * math.pi / 180., includeBoundary,
                                     forceParametrizablePatches,
                                     curveAngle * math.pi / 180.)

    # Create a geometry for all the discrete curves and surfaces in the mesh, by
    # computing a parametrization for each one
    gmsh.model.mesh.createGeometry()
    # Create a volume from all the surfaces
    s = gmsh.model.getEntities(2)
    l = gmsh.model.geo.addSurfaceLoop([e[1] for e in s])
    gmsh.model.geo.addVolume([l])

    gmsh.model.geo.synchronize()

    # We specify element sizes imposed by a size field, just because we can :-)
    f = gmsh.model.mesh.field.add("MathEval")
    if gmsh.onelab.getNumber('Parameters/Apply funny mesh size field?')[0]:
        gmsh.model.mesh.field.setString(f, "F", "2*Sin((x+y)/5) + 3")
    else:
        gmsh.model.mesh.field.setString(f, "F", "4")
    gmsh.model.mesh.field.setAsBackgroundMesh(f)

    gmsh.model.mesh.generate(3)
    gmsh.write('t13.msh')

# Create ONELAB parameters with remeshing options:
gmsh.onelab.set("""[
  {
    "type":"number",
    "name":"Parameters/Angle for surface detection",
    "values":[40],
    "min":20,
    "max":120,
    "step":1
  },
  {
    "type":"number",
    "name":"Parameters/Create surfaces guaranteed to be parametrizable",
    "values":[0],
    "choices":[0, 1]
  },
  {
    "type":"number",
    "name":"Parameters/Apply funny mesh size field?",
    "values":[0],
    "choices":[0, 1]
  }
]""")

gmsh.option.setNumber("Mesh.MeshSizeFactor", 10)
gmsh.option.setNumber("Mesh.ToleranceInitialDelaunay", 1e-12)
gmsh.option.setNumber("Mesh.CharacteristicLengthFromCurvature", 1)

# Create the geometry and mesh it:
createGeometryAndMesh()

# Launch the GUI and handle the "check" event to recreate the geometry and mesh
# with new parameters if necessary:
def checkForEvent():
    action = gmsh.onelab.getString("ONELAB/Action")
    if len(action) and action[0] == "check":
        gmsh.onelab.setString("ONELAB/Action", [""])
        createGeometryAndMesh()
        gmsh.graphics.draw()
    return True

if "-nopopup" not in sys.argv:
    gmsh.fltk.initialize()
    while gmsh.fltk.isAvailable() and checkForEvent():
        gmsh.fltk.wait()

gmsh.finalize()
