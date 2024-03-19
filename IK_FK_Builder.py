import maya.cmds as cmds 
from . import Curve 

# Importing the Curve module for creating customized curves.

def makeFingerRig( bindJoints, optionCurve = None, poleVectorPreset = Curve.PRESET_TRIANGLE, 
                   ikControlPreset = Curve.PRESET_TRIANGLE, fkControlPreset= Curve.PRESET_SQUARE,  
                   controlSize = 1, fkControlColor = Curve.RED, ikControlColor = Curve.BLUE ):  
    """ 
      
    Create an IK/FK Chain for finger rigging.

    This function automates the process of creating an IK/FK Chain for rigging in Maya! It takes a list of three joints
    representing the finger, arm, or any three hierarchy joints and generates IK / FK controls. Users can specify various parameters
    such as the option curve, control sizes, and colors to customize the rig according to fit their needs.

    Parameters:
    - bindJoints (list): A list of joint names representing the joints.
    - optionCurve (str, optional): Name of the option curve. Defaults to None.
    - poleVectorPreset (str, optional): Preset for the pole vector curve. Defaults to Curve.PRESET_TRIANGLE.
    - ikControlPreset (str, optional): Preset for the IK control curve. Defaults to Curve.PRESET_TRIANGLE.
    - fkControlPreset (str, optional): Preset for the FK control curve. Defaults to Curve.PRESET_SQUARE.
    - controlSize (float, optional): Size of the control curves. Defaults to 1.
    - fkControlColor (tuple, optional): RGB color for the FK control curve. Defaults to Curve.RED.
    - ikControlColor (tuple, optional): RGB color for the IK control curve. Defaults to Curve.BLUE
    
    """
    
    rootGrp = cmds.createNode('transform')
    rootGrp = cmds.rename(rootGrp, 'somethingCool')
    ikChain = []
    fkControls = []
    curParent = rootGrp             # Current parent joint
    curveParent  = rootGrp          # Parent for curve 
    
    # Create FK controls and IK joint rig
    for node in bindJoints:
        NewJoint = cmds.createNode( 'joint' )
        
        # Parent under previous joint
        if curParent is not None:
            print ("REPARENT:", curParent)
            NewJoint = cmds.parent(NewJoint, curParent)[0]
            
        # Rename joint with IK prefix
        NewJoint = cmds.rename( NewJoint , 'IK_{0}'.format(node) )
        
        # Match Transform BIND JOINT to NEW JOINT
        cmds.matchTransform(NewJoint, node, position =True, rotation = True)
        
        # Set preferred angle from current rotation
        for xyz in 'XYZ':
            val = cmds.getAttr( '{0}.rotate{1}'.format(NewJoint, xyz) )
            cmds.setAttr( '{0}.preferredAngle{1}'.format(NewJoint, xyz), val )
            
        ikChain.append(NewJoint)
        curParent =  NewJoint
 
        # Create curve
        fkCurve = Curve.create(name = '{0}_FK_ctrl'.format(node), preset = fkControlPreset, 
                               size = controlSize, parent = None, color = fkControlColor )
                               
        # Lock and hide attributes
        lockHideAttrs(fkCurve, rotate = False)
        
        # Create off set group for FK curve ctrl
        fkCurveGrp = cmds.group(fkCurve)
        fkCurveGrp =cmds.rename( fkCurveGrp, '{0}_os'.format(fkCurve) )
        
        # Match FK curve to FK joint
        cmds.matchTransform( fkCurveGrp, NewJoint, position = True, rotation = True) 
        
        # Parent FK curve to FK joint
        if curveParent is not None:
            fkCurveGrp = cmds.parent( fkCurveGrp, curveParent)[0]
            
        # Put the group under curve
        curveParent = fkCurve
        fkControls.append(fkCurve)
        
    # Create IK Curves (Pole Vector and Wrist Ctrl) 
    PoleVectorCurve = Curve.create(name = 'ikPoleVectorCurve', preset = poleVectorPreset,
                                   size = controlSize, parent = None, color = ikControlColor )
                                   
    lockHideAttrs(PoleVectorCurve, translate = False)
    
    ikWristCurve = Curve.create(name = 'ikWristCurve', preset = ikControlPreset,
                                size = controlSize, parent = None, color = ikControlColor )
                                
    lockHideAttrs(ikWristCurve, translate = False, rotate = False)
    
    # Orient constraint curve to IK finger end
    cmds.orientConstraint(ikWristCurve, ikChain[-1])
    
    # Match Transforms IK Curves to IK Handle
    cmds.matchTransform(ikWristCurve, ikChain[-1])
    cmds.matchTransform(PoleVectorCurve, ikChain[1])
    
    # Create IK Handle
    result = cmds.ikHandle(startJoint = ikChain[0], endEffector = ikChain[-1], solver = 'ikRPsolver' )
    ikHandleFinger, effFinger = result
    ikHandleFinger = cmds.rename(ikHandleFinger, 'ikHandleFinger')
    cmds.parent(ikHandleFinger, ikWristCurve)
    
    # Constraint PoleVector to IK Handle
    cmds.poleVectorConstraint(PoleVectorCurve, ikHandleFinger)
    
    # Get option box with FK IK Switch Attribute
    if optionCurve is None: 
        optionCurve = Curve.create(name = 'SwitchFinger', preset = fkControlPreset,
                                   size = controlSize, parent = rootGrp, color = fkControlColor )
                                   
    attrSwitchName = 'fkIkSwitch'
    
    if not cmds.attributeQuery( attrSwitchName, node= optionCurve, exists = True ):
        # Create the attribute 
        cmds.addAttr( optionCurve, longName = attrSwitchName, defaultValue = 0,
                      minValue = 0, maxValue = 1, attributeType = "double", keyable = True)
                      
    attrSwitch = '{0}.{1}'.format(optionCurve, attrSwitchName)
 
    # Make Reverse Node
    revNode = cmds.createNode( "reverse" )
    revNode = cmds.rename( revNode, '{0}_IK_FK_reverse'.format(optionCurve) )
    cmds.connectAttr(attrSwitch, '{0}.inputX'.format(revNode), force=True)
    attrRev = '{0}.outputX'.format(revNode)
    
    # Constraint FK curves and IK Joints to the Bind Joints and get constraints
    for fkControl, ikJoint, bindJoint in zip (fkControls, ikChain, bindJoints): 
        cnst = cmds.orientConstraint(fkControl, ikJoint, bindJoint)
        weightAttrs = cmds.orientConstraint(cnst[0], weightAliasList = True, query = True )
        cmds.connectAttr(attrSwitch, '{0}.{1}'.format(cnst[0], weightAttrs[0]), force =True )
        cmds.connectAttr(attrRev, '{0}.{1}'.format(cnst[0], weightAttrs[1]), force = True )
        print(weightAttr)
        
    # Hook up visibility 
    for node in [ikWristCurve, PoleVectorCurve]:
        for shape in cmds.listRelatives( node, shapes = True, fullPath = True ):    
            cmds.connectAttr(attrRev, '{0}.visibility'.format(shape), force=True)
            
    for fkControl in fkControls:
        for shape in cmds.listRelatives( fkControl, shapes = True, fullPath = True ):
            cmds.connectAttr(attrSwitch, '{0}.visibility'.format(shape), force = True)
            
# Lock and hide attributes
def lockHideAttrs (node, visibility = True, scale = True, rotate = True, translate = True):
    if visibility:
        cmds.setAttr( '{0}.visibility'.format(node), lock = True, keyable = False)
    for srt, do  in [('scale',scale), ('rotate', rotate), ('translate', translate) ]:
        if do:
            for xyz in 'XYZ':
                cmds.setAttr( '{0}.{1}{2}'.format(node,srt, xyz), lock = True, keyable = False)

# Entry Point
curSel = cmds.ls(selection = True)

if len(curSel) >= 3:
    bindJoints  = curSel[:3]
    optionCurve = curSel[3] if len(curSel) >3 else None
    makeFingerRig( bindJoints = bindJoints, optionCurve = optionCurve )