import maya.cmds as cmds

RED = [1.0, 0.0, 0.0]
GREEN = [0.0, 1.0, 0.0]
BLUE = [0.0, 0.0, 1.0]

PRESET_TRIANGLE = 'triangle'
PRESET_SQUARE = 'square'

#######################################################################################################################################################################

def create(name = 'curve', preset = 'square', size = 1, parent = None, color = None ):
    """ Create a New Curve Control
        RETURN Name of the New Curve
        
    name     <str>     NAME of the New Curve that is Created 
    preset   <str>     TYPE of Curve to Create
                        square | triangle 
    size     <float>   size of the new Curve
    parent   <str>     Name of the Node to make the Curve of a child of...
    """
    if preset == 'triangle':
        # Define a Triangle Curve 
        degree = 1 
        point = [(-1,0,-1),(1,0,-1), (0,0,1), (-1,0,-1)] 
        knots = [0, 1, 2, 3]
    else:
        # Define curve a Square Curve 
        degree = 1 
        point = [(-1,0,1),(-1,0,-1), (1,0,-1), (1,0,1), (-1,0,1)] 
        knots = [0, 1, 2, 3, 4]

    # Resize the Curve Points
    resizedPoints = []
    for points in point:
        resizedPoint = [points[0]*size, points[1]*size, points[2]*size]
        resizedPoints.append( resizedPoint )
    
    # Creating Curve
    awesome_curve = cmds.curve( point = resizedPoints, degree = degree, knot = knots)

    # Rename Curve
    awesome_curve = cmds.rename( awesome_curve, name)

    # Reparent ?
    if parent is not None and cmds.objExists(parent):
        awesome_curve = cmds.parent( awesome_curve, parent )[0]
        
    # Colorize the Curve
    if color is not None:
        cmds.color( awesome_curve, rgb = color)


    # Return the Curve Name
    return awesome_curve



#######################################################################################################################################################################

def doTool( targets = None, preset = 'square', suffix = '_ctrl', color = None  ):
    """Interative Curve Creating TOOL.
    
    targets <[str]>     List of Nodes to create a Curve For...
            <[bool]>    If TRUE, Create a Curve for everything in the Scene Selection.
    
    """
    
    # Validate our TARGETS
    if targets is True: 
        # We are going to get current selection 
        targets = cmds.ls(selection = True)
    elif isinstance(targets, str): 
        targets = [targets] 
    
    if not isinstance(targets, list):
        print("IMPROPER Targets Supplied!")    
        cmds.inViewMessage( amg='Warning <hl>"improper Targets Supplied! "</hl>.', pos='midCenter', fade=True )
        return result 
    
    
    
    result = []
    if targets is not None:
        for target in targets:
            if not (isinstance(target,str) and cmds.objExists(target) ):
                print("Target Doesnt Exsit:", target)
                cmds.inViewMessage( amg='Warning <hl>"improper targets supplied! :( "</hl>.', pos='midCenter', fade=True )
                continue 
            #Get the SHAPE...
            shapes = cmds.listRelatives(target, shapes = True, path = True)
            #Determine a good size for the curve
            size = 1
            if shapes is not None:
                shape = shapes[0]
                #Bounding box is as list [xSize. ySize, zSize] 
                bbSize = cmds.getAttr(shape + '.boundingBoxSize') 
                size = bbSize[0][0] # Use the xSize
                size = size/1.8     # Use half the size
                
             #Create the new Curve
            awesome_curve = create(name = target + suffix,
                                   preset = preset,
                                   size = size, 
                                   parent = None, 
                                   color = color)
            # Match the transform
            cmds.matchTransform ( awesome_curve, target)
            
            # Add the new curve to the result list 
            result.append(awesome_curve)
    return result
    
         
  

#######################################################################################################################################################################
def createFKChain( numberOfControls = 1, length = 10, nestChildControls = False, 
                   name = 'curve', preset = 'square', size = 1, parent = None, color = None):
                   
    """Creating FK Chaing Tool.
    
    targets <[numberOfControls]>     List of Controls
            <[length]>               Length of the ribbon
    
    """

    result = []


    if numberOfControls < 1: 
        cmds.inViewMessage( amg='Warning <hl>"improper targets supplied! :( "</hl>.', pos='midCenter', fade=True )
        return result
 
    # NOW, we can ITERATE (LOOP) and CREATE A CONTROL until we reach the numberOfControls
    current_x_value = 0
    
    if numberOfControls > 1:
        delta_x = length /(numberOfControls-1)
    else:
        delta_x = 0
   
    current_parent = parent 
    for i in range(numberOfControls):
        new_curve = create(name = name, preset = preset, size = size, parent = current_parent, color = color) 
        result.append ( new_curve )
        # POSITION the NEW CURVE
        cmds.setAttr (new_curve + ".translateX",current_x_value)
        if nestChildControls == True:
            current_x_value = delta_x
            # UPDATE the current parent
            current_parent = new_curve 
        else:
            current_x_value = current_x_value + delta_x 
        
    return result  
    
    