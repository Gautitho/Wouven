FILE="data/spells/xelor.json"
# allowedTargetList
sed -i 's/"allowedTargetList" : \[\(.*\)"all"\(.*\)\]/"allowedTargetList" : \[\1{}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"emptyTile"\(.*\)\]/"allowedTargetList" : \[\1{"empty" : "True"}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"allEntity"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True"}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"allOrganic"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "noTypeList" : ["mechanism"]}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"myEntity"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "team" : "my"}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"myOrganic"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "team" : "my", "noTypeList" : ["mechanism"]}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"opEntity"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "team" : "op"}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"opOrganic"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "team" : "op", "noTypeList" : ["mechanism"]}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"myHero"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "main" : "hero", "team" : "my"}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"opHero"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "main" : "hero", "team" : "op"}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"allOrganicAligned"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "main" : "aligned", "noTypeList" : ["mechanism"]}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"allFirstEntityAligned"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "main" : "firstAligned"}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"allFirstOrganicAligned"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "main" : "firstAligned", "noTypeList" : ["mechanism"]}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"heroAdjacentTile"\(.*\)\]/"allowedTargetList" : \[\1{"main" : "adjacent"}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"allOrganicAdjacent"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "main" : "adjacent"}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"firstTargetAdjacentTile"\(.*\)\]/"allowedTargetList" : \[\1{"main" : "adjacent", "ref" : "firstTarget"}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"emptyAlignedTile"\(.*\)\]/"allowedTargetList" : \[\1{"empty" : "True", "main" : "aligned"}\2\]/g' $FILE
sed -i 's/"allowedTargetList" : \[\(.*\)"self"\(.*\)\]/"allowedTargetList" : \[\1{"entity" : "True", "main" : "self"}\2\]/g' $FILE
# target
sed -i 's/\(^[ ]*\)"target"\(.*\) : "target"/\1"target"\2 : {}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "self"/\1"target"\2 : {"main" : "self"}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "myPlayer"/\1"target"\2 : {"main" : "player", "team" : "my"}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "opPlayer"/\1"target"\2 : {"main" : "player", "team" : "op"}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "targetPlayer"/\1"target"\2 : {"main" : "player", "team" : "target"}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "myHero"/\1"target"\2 : {"main" : "hero", "team" : "my"}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "opHero"/\1"target"\2 : {"main" : "hero", "team" : "op"}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "allOrganicAroundSelf"/\1"target"\2 : {"main" : "around", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "myOrganicAroundSelf"/\1"target"\2 : {"main" : "around", "team" : "my", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "opOrganicAroundSelf"/\1"target"\2 : {"main" : "around", "team" : "op", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "allOrganicAroundTarget"/\1"target"\2 : {"main" : "around", "ref" : "target", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "opOrganicAroundTarget"/\1"target"\2 : {"main" : "around", "team" : "op", "ref" : "target", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "myOrganicAroundTarget"/\1"target"\2 : {"main" : "around", "team" : "my", "ref" : "target", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "allOrganicAdjacentToSelf"/\1"target"\2 : {"main" : "adjacent", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "allOrganicAdjacentToFirstTarget"/\1"target"\2 : {"main" : "adjacent", "ref" : "target", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "opOrganicFirstCrossSelf"/\1"target"\2 : {"main" : "firstAligned", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "opBoard"/\1"target"\2 : {"main" : "board", "team" : "op", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "myBoard"/\1"target"\2 : {"main" : "board", "team" : "my", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "opOrganicWithHighestPv"/\1"target"\2 : {"main" : "highestPv", "team" : "op", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "currentSpell"/\1"target"\2 : {"main" : "currentSpell"}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "hand"/\1"target"\2 : {"main" : "hand"}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "allOrganicCrossSelf"/\1"target"\2 : {"main" : "cross", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "opOrganicCrossSelf"/\1"target"\2 : {"main" : "cross", "team" : "op", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "opOrganicAligned"/\1"target"\2 : {"main" : "aligned", "team" : "op", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "allOrganicAligned"/\1"target"\2 : {"main" : "aligned", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "allOrganicAligned:\(.*\)"/\1"target"\2 : {"main" : "aligned", "range" : "\3", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "opOrganicAligned:\(.*\)"/\1"target"\2 : {"main" : "aligned", "team" : "op", "range" : "\3", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "allOrganicCross:\(.*\)"/\1"target"\2 : {"main" : "cross", "ref" : "target", "range" : "\3", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "myOrganicCross:\(.*\)"/\1"target"\2 : {"main" : "cross", "team" : "my", "ref" : "target", "range" : "\3", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "opOrganicCrossSelf:\(.*\)"/\1"target"\2 : {"main" : "cross", "team" : "op", "range" : "\3", "noTypeList" : ["mechanism"]}/g' $FILE
sed -i 's/\(^[ ]*\)"target"\(.*\) : "allOrganicCrossSelf:\(.*\)"/\1"target"\2 : {"main" : "cross", "range" : "\3", "noTypeList" : ["mechanism"]}/g' $FILE