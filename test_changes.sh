PLASMOID_NAME=kliqtune

zip -r ../$PLASMOID_NAME.plasmoid .
plasmapkg -r $PLASMOID_NAME
plasmapkg -i ../$PLASMOID_NAME.plasmoid

sleep 4 
plasmoidviewer $PLASMOID_NAME
