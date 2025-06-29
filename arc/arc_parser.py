import bpy
import addon_utils

import struct
import zlib
import os
import sys
from glob import glob
import ctypes
import numpy as np
import shutil
import json

import logging
logger = logging.getLogger("mhst2_import")

def jamcrc(string):
    return (zlib.crc32(str(string).encode()) ^ 0xffffffff) & 0x7fffffff

fileExts = {}
fileExts[jamcrc("rBattleBinary")] = ".btb"
fileExts[jamcrc("rBattleCutCmdData")] = ".bccmd"
fileExts[jamcrc("rBattleSelectSetData")] = ".bsset"
fileExts[jamcrc("rAgingFieldPatrolDataNative")] = ".afpd"
fileExts[jamcrc("rTalkDemoCut")] = ".cut"
fileExts[jamcrc("rTalkDemoSound")] = ".tsnd"
fileExts[jamcrc("rTalkDemoWorkOriginInfo")] = ".work"
fileExts[jamcrc("rTalkDemoObjInitPos")] = ".pos"
fileExts[jamcrc("rFieldEnemyDefaultAifsmDataNaitive")] = ".fedad"
fileExts[jamcrc("rFieldConnectionInfoNative")] = ".fci"
fileExts[jamcrc("rFieldPartsInfoNative")] = ".fpi"
fileExts[jamcrc("rFieldPartsLayoutNative")] = ".fpl"
fileExts[jamcrc("rTraceSonarNative")] = ".ts"
fileExts[jamcrc("rFieldPlacementObjectSetNative")] = ".fpos"
fileExts[jamcrc("rFieldCamOption")] = ".fco"
fileExts[jamcrc("rDungeonInfoListNative")] = ".dai"
fileExts[jamcrc("rFieldNpcNekoTaxiList")] = ".fntl"
fileExts[jamcrc("rFieldObjectList")] = ".fol"
fileExts[jamcrc("rFieldCamera")] = ".fcr"
fileExts[jamcrc("rOccluder2Native")] = ".occ2"
fileExts[jamcrc("rInstanceDrawDistance")] = ".idd"
fileExts[jamcrc("rIDColor")] = ".idcol"
fileExts[jamcrc("rInstancePlacement")] = ".ipr"
fileExts[jamcrc("rPlayerMoveConfigData")] = ".pmc"
fileExts[jamcrc("rSoundGuiSe")] = ".sgs"
fileExts[jamcrc("rSoundParamOffsetControl")] = ".spoc"
fileExts[jamcrc("rSoundPelTiedSe")] = ".pts"
fileExts[jamcrc("rSoundAreaReverb")] = ".sar"
fileExts[jamcrc("rSoundSystemSetting")] = ".sss"
fileExts[jamcrc("rSoundPronounceList")] = ".sptl"
fileExts[jamcrc("rEnaJoinProgressDataNative")] = ".ejpd"
fileExts[jamcrc("rKizunaLvProgressDataNative")] = ".klpd"
fileExts[jamcrc("rReusJoinProgressDataNative")] = ".rjpd"
fileExts[jamcrc("rFieldDirectionInfoNative")] = ".fdi"
fileExts[jamcrc("rAgingBtlBuddyTableNative")] = ".abbt"
fileExts[jamcrc("rAgingBtlEnemySetTableNative")] = ".abest"
fileExts[jamcrc("rAgingBtlStageTableNative")] = ".abst"
fileExts[jamcrc("rAgingCheckBuddyNative")] = ".acb"
fileExts[jamcrc("rAgingCheckEnaLayArmorNative")] = ".acela"
fileExts[jamcrc("rAgingCheckNaviAccesoryNative")] = ".acna"
fileExts[jamcrc("rAgingCheckPlArmorNative")] = ".acpa"
fileExts[jamcrc("rAgingCheckWeaponNative")] = ".acwp"
fileExts[jamcrc("rAgingFieldTableNative")] = ".aft"
fileExts[jamcrc("rCheatCheckTableItemBattleNative")] = ".cctib"
fileExts[jamcrc("rCheatCheckTableWeaponBowNative")] = ".cctbw"
fileExts[jamcrc("rCheatCheckTableWeaponGunNative")] = ".cctgn"
fileExts[jamcrc("rDoubleKizunaCameraOffsetNative")] = ".bdkc"
fileExts[jamcrc("rDoubleKizunaMonsterConditionNative")] = ".bdkmc"
fileExts[jamcrc("rDoubleKizunaMonsterOffsetNative")] = ".bdkm"
fileExts[jamcrc("rDoubleKizunaSchedulerPathNative")] = ".bdkd"
fileExts[jamcrc("rActionCommandDelayTimeDataNative")] = ".acdd"
fileExts[jamcrc("rAnimationSecondParamNative")] = ".asp"
fileExts[jamcrc("rGuiClearedDungeonItemParamNative")] = ".cdi"
fileExts[jamcrc("rGuiColorDataNative")] = ".gcol"
fileExts[jamcrc("rGuiFadeDataNative")] = ".gfad"
fileExts[jamcrc("rGuiHatchBabyParamNative")] = ".ghbp"
fileExts[jamcrc("rGuiModelDrawCameraParamNative")] = ".gmdc"
fileExts[jamcrc("rGuiModelDrawWindowParamNative")] = ".gmdw"
fileExts[jamcrc("rGuiMonsterModelParamNative")] = ".gmmp"
fileExts[jamcrc("rGuiMultiVsPlayerParamNative")] = ".gmvp"
fileExts[jamcrc("rGuiNpcModelParamNative")] = ".gnpc"
fileExts[jamcrc("rGuiParamNative")] = ".gpm"
fileExts[jamcrc("rGuiRiderCardBuddyParamNative")] = ".grcb"
fileExts[jamcrc("rGuiStatusPlayerParamNative")] = ".gspp"
fileExts[jamcrc("rGuiTraditionBuddyParamNative")] = ".gtbp"
fileExts[jamcrc("rGuiWeaponModelParamNative")] = ".gwmp"
fileExts[jamcrc("rAchievementIconNative")] = ".aic"
fileExts[jamcrc("rCommandIconNative")] = ".cic"
fileExts[jamcrc("rIconStatusDataNative")] = ".isd"
fileExts[jamcrc("rItemIconNative")] = ".iic"
fileExts[jamcrc("rMonsterIconNative")] = ".mic"
fileExts[jamcrc("rSkillIconNative")] = ".sic"
fileExts[jamcrc("rDramaMessageDataNative")] = ".drmd"
fileExts[jamcrc("rFieldCommonMessageDataNative")] = ".fcmd"
fileExts[jamcrc("rGameMessageDataNative")] = ".grmd"
fileExts[jamcrc("rNpcMessageDataNative")] = ".ntlkd"
fileExts[jamcrc("rTalkMessageDataNative")] = ".tlkd"
fileExts[jamcrc("rOptionKeyConfigButtonDataNative")] = ".okbd"
fileExts[jamcrc("rOptionKeyConfigDataNative")] = ".okd"
fileExts[jamcrc("rOptionKeyConfigKeyboardDataNative")] = ".okkd"
fileExts[jamcrc("rOptionLanguageDataNative")] = ".lad"
fileExts[jamcrc("rOptionParamDataNative")] = ".opd"
fileExts[jamcrc("rOptionSettingDataNative")] = ".osd"
fileExts[jamcrc("rAmiiboGiftNative")] = ".agt"
fileExts[jamcrc("rBattleBuddyConditionDataNative")] = ".bbcnd"
fileExts[jamcrc("rBattleCmdCameraDataNative")] = ".bccam"
fileExts[jamcrc("rBattleCmdIgnoreEnemyDataNative")] = ".bcige"
fileExts[jamcrc("rBattleEffHitInfoDataNative")] = ".behi"
fileExts[jamcrc("rBattleEnemyMCTblNative")] = ".bemct"
fileExts[jamcrc("rBattleEventResourceDataNative")] = ".bert"
fileExts[jamcrc("rBattleEventResultDataNative")] = ".berd"
fileExts[jamcrc("rBattleEventTblNative")] = ".bet"
fileExts[jamcrc("rBattleMorphChangeDataNative")] = ".bmcd"
fileExts[jamcrc("rBattleMorphConditionDataNative")] = ".bmcnd"
fileExts[jamcrc("rBattleNavirouFsmTableNative")] = ".bnft"
fileExts[jamcrc("rBattleNavirouMessageNative")] = ".bnmt"
fileExts[jamcrc("rBattleNavirouSetTableNative")] = ".bnst"
fileExts[jamcrc("rBattleNavirouUniqueNative")] = ".bnut"
fileExts[jamcrc("rBattlePartsConditionDataNative")] = ".bptcnd"
fileExts[jamcrc("rBCATAppDataNative")] = ".bcatData"
fileExts[jamcrc("rBingoBonusCategoryNative")] = ".bbc"
fileExts[jamcrc("rBreakFieldObjectDataNative")] = ".bfofd"
fileExts[jamcrc("rBuddyBtlMCDataNative")] = ".bdbcm"
fileExts[jamcrc("rCharaCustomLogDataNative")] = ".chcl"
fileExts[jamcrc("rCharaRemakeTicketDataNative")] = ".crd"
fileExts[jamcrc("rDemoGalleryDataNative")] = ".dgd"
fileExts[jamcrc("rDifficultyConvertCountNative")] = ".dcc"
fileExts[jamcrc("rDifficultyConvertGameFlagNative")] = ".dcgf"
fileExts[jamcrc("rDLCAppDataNative")] = ".dlcData"
fileExts[jamcrc("rDLCViewDataNative")] = ".dlcView"
fileExts[jamcrc("rDungeonChestLotTableNative")] = ".dclt"
fileExts[jamcrc("rDungeonContainsDataNative")] = ".dcd"
fileExts[jamcrc("rDungeonCreatePatternNative")] = ".dcp"
fileExts[jamcrc("rDungeonEggMonsterDataNative")] = ".demd"
fileExts[jamcrc("rDungeonEnemyFixedDataNative")] = ".defd"
fileExts[jamcrc("rDungeonEnemyHomingDataNative")] = ".deh"
fileExts[jamcrc("rDungeonEnemyLocatorDataNative")] = ".deloc"
fileExts[jamcrc("rDungeonEnemyLotDataNative")] = ".deld"
fileExts[jamcrc("rDungeonNestRarenessDataNative")] = ".dnrd"
fileExts[jamcrc("rEggUniquePatternDataNative")] = ".eup"
fileExts[jamcrc("rEnvCreatureDataNative")] = ".ecr"
fileExts[jamcrc("rExpeditionFieldDataNative")] = ".exfd"
fileExts[jamcrc("rExpeditionPolicyDataNative")] = ".expl"
fileExts[jamcrc("rExpeditionSlotNumDataNative")] = ".esd"
fileExts[jamcrc("rFieldAmbientDataNative")] = ".fldamb"
fileExts[jamcrc("rFieldPartsDataNative")] = ".fpd"
fileExts[jamcrc("rFieldPartsNameDataNative")] = ".fldpn"
fileExts[jamcrc("rFieldSkyDataNative")] = ".fldsky"
fileExts[jamcrc("rFieldSpotDataNative")] = ".flds"
fileExts[jamcrc("rFixedDungeonConfigDataNative")] = ".fdcd"
fileExts[jamcrc("rFortuneGiftNative")] = ".fgt"
fileExts[jamcrc("rGeneRandomSetNative")] = ".grset"
fileExts[jamcrc("rGiftBuddyTableNative")] = ".tgb"
fileExts[jamcrc("rGiftEggTableNative")] = ".tge"
fileExts[jamcrc("rGuiFontDataNative")] = ".fnd"
fileExts[jamcrc("rGuiFontLanguageDataNative")] = ".gfld"
fileExts[jamcrc("rGuiLocalizeTextureDataNative")] = ".ltd"
fileExts[jamcrc("rGuiMessageDataNative")] = ".msgm"
fileExts[jamcrc("rGuiWorldMapNative")] = ".gwm"
fileExts[jamcrc("rHabitatDataNative")] = ".hbt"
fileExts[jamcrc("rHardDungeonUIDataNative")] = ".hdu"
fileExts[jamcrc("rHatchEggBonusDataNative")] = ".heb"
fileExts[jamcrc("rEditCameraDataNative")] = ".ecd"
fileExts[jamcrc("rEditColorPresetDataNative")] = ".ecp"
fileExts[jamcrc("rEditEyeShapeDataNative")] = ".eed"
fileExts[jamcrc("rEditFaceShapeDataNative")] = ".efd"
fileExts[jamcrc("rEditHairstyleDataNative")] = ".ehd"
fileExts[jamcrc("rEditMakeupTypeDataNative")] = ".emad"
fileExts[jamcrc("rEditMouthShapeDataNative")] = ".emod"
fileExts[jamcrc("rEditParamDataNative")] = ".epd"
fileExts[jamcrc("rEditVoiceTypeDataNative")] = ".evd"
fileExts[jamcrc("rLinkedDungeonDataNative")] = ".ldd"
fileExts[jamcrc("rMelynxShopAccessoryDataNative")] = ".macd"
fileExts[jamcrc("rMelynxShopArmorDataNative")] = ".mard"
fileExts[jamcrc("rMelynxShopDataNative")] = ".msp"
fileExts[jamcrc("rMelynxShopWeaponDataNative")] = ".mwd"
fileExts[jamcrc("rMenuRiderNoteDataNative")] = ".mrnd"
fileExts[jamcrc("rModTextureNoScaleDataNative")] = ".mtnscl"
fileExts[jamcrc("rMonsterAdditionalShowTableNative")] = ".mas"
fileExts[jamcrc("rMonsterBaseInfoDataNative")] = ".mbi"
fileExts[jamcrc("rMHSoundEmitter")] = ".ses"
fileExts[jamcrc("rMHSoundSequence")] = ".mss"
fileExts[jamcrc("rSoundAttributeSe")] = ".aser"
fileExts[jamcrc("rSoundEngine")] = ".engr"
fileExts[jamcrc("rSoundEngineXml")] = ".engr.xml"
fileExts[jamcrc("rSoundEngineValue")] = ".egvr"
fileExts[jamcrc("rSoundMotionSe")] = ".mser"
fileExts[jamcrc("rSoundSequenceSe")] = ".ssqr"
fileExts[jamcrc("rSoundSimpleCurve")] = ".sscr"
fileExts[jamcrc("rSoundSubMixerXml")] = ".smxr.xml"
fileExts[jamcrc("rSoundSubMixer")] = ".smxr"
fileExts[jamcrc("uSoundSubMixer::CurrentSubMixer")] = ".smxr"
fileExts[jamcrc("rMonsterPartsTableNative")] = ".mpt"
fileExts[jamcrc("rNavirouGuideDataNative")] = ".ngt"
fileExts[jamcrc("rNpc2dFaceTexTableNative")] = ".nft"
fileExts[jamcrc("rNpcAirouSetMotionDataNative")] = ".nasmd"
fileExts[jamcrc("rNpcLayeredArmorDataNative")] = ".nlad"
fileExts[jamcrc("rNpcSetMotionDataNative")] = ".nsmd"
fileExts[jamcrc("rNpcTalkResourceDataNative")] = ".ntrp"
fileExts[jamcrc("rNpcTalkZoneNative")] = ".ntz"
fileExts[jamcrc("rPotEffectDataNative")] = ".pte"
fileExts[jamcrc("rPotLevelDataNative")] = ".ptl"
fileExts[jamcrc("rPotOfferingDataNative")] = ".pto"
fileExts[jamcrc("rPotPrayingDataNative")] = ".ptp"
fileExts[jamcrc("rPresetParamCharaCustomNative")] = ".tppcc"
fileExts[jamcrc("rPresetParamLearningSkillSetNative")] = ".tppls"
fileExts[jamcrc("rPresetParamOtomonNative")] = ".tppo"
fileExts[jamcrc("rPresetParamOtomonGeneNative")] = ".tppog"
fileExts[jamcrc("rRiderNoteDataRushNative")] = ".rndr"
fileExts[jamcrc("rRideSkillTableNative")] = ".rst"
fileExts[jamcrc("rSkillCalcNative")] = ".skc"
fileExts[jamcrc("rSkillSetDataNative")] = ".wss"
fileExts[jamcrc("rStableCapacityDataNative")] = ".scd"
fileExts[jamcrc("rStatusChangeFlagsNative")] = ".scf"
fileExts[jamcrc("rStatusDataNative")] = ".sdt"
fileExts[jamcrc("rStoryQuestDataNative")] = ".sqd"
fileExts[jamcrc("rStoryQuestDefineNative")] = ".sqdf"
fileExts[jamcrc("rSubQuestConditionDataNative")] = ".sqccd"
fileExts[jamcrc("rSubQuestDataRenewNative")] = ".suqd"
fileExts[jamcrc("rSubQuestVeilDataNative")] = ".svd"
fileExts[jamcrc("rSubstituteNpcTblNative")] = ".sntt"
fileExts[jamcrc("rSummaryDataNative")] = ".smr"
fileExts[jamcrc("rTalkDemoDefineDataNative")] = ".tdmspk"
fileExts[jamcrc("rTrialCleanNativeDataNative")] = ".tcn"
fileExts[jamcrc("rTutorialArrowDataNative")] = ".tad"
fileExts[jamcrc("rTutorialLockDataNative")] = ".tld"
fileExts[jamcrc("rVsItemSetDataNative")] = ".vsitemset"
fileExts[jamcrc("rVsPrizeDataNative")] = ".vsprize"
fileExts[jamcrc("rVsRuleDataNative")] = ".vsrule"
fileExts[jamcrc("rSoundDemoControlNative")] = ".sdc"
fileExts[jamcrc("rSoundDemoEnvControlNative")] = ".sdec"
fileExts[jamcrc("rSoundDemoSeControlNative")] = ".sdsc"
fileExts[jamcrc("rSoundGuiOperationNative")] = ".sgo"
fileExts[jamcrc("rSoundInfoSeNative")] = ".siet"
fileExts[jamcrc("rSoundInfoStreamNative")] = ".siets"
fileExts[jamcrc("rSoundArchiveDataNative")] = ".samd"
fileExts[jamcrc("rSoundArmorDataNative")] = ".sad"
fileExts[jamcrc("rSoundBattleStageDataNative")] = ".sbsd"
fileExts[jamcrc("rSoundBattleStageDefineNative")] = ".sbsdef"
fileExts[jamcrc("rSoundBgmMonsterDataNative")] = ".sbmd"
fileExts[jamcrc("rSoundFootstepDataNative")] = ".sftd"
fileExts[jamcrc("rSoundFSMCommandBgmDataNative")] = ".sfcbd"
fileExts[jamcrc("rSoundFSMCommandSeDataNative")] = ".sfcsd"
fileExts[jamcrc("rSoundMonsterDataNative")] = ".smd"
fileExts[jamcrc("rSoundMonsterEnvironmentalDataNative")] = ".smed"
fileExts[jamcrc("rSoundMonsterKizunaDataNative")] = ".smkd"
fileExts[jamcrc("rSoundNpcAirouDataNative")] = ".snad"
fileExts[jamcrc("rSoundNpcDataNative")] = ".snd"
fileExts[jamcrc("rSoundObjectDataNative")] = ".sod"
fileExts[jamcrc("rSoundSceneVolumeNative")] = ".ssv"
fileExts[jamcrc("rSoundWeaponDataNative")] = ".swd"
fileExts[jamcrc("rSoundNpcVoicePathDataNative")] = ".snvpd"
fileExts[jamcrc("rSoundPlayerVoicePathDataNative")] = ".spvpd"
fileExts[jamcrc("rUnlockMixDataNative")] = ".ulm"
fileExts[jamcrc("rUnlockProgressDataNative")] = ".ulp"
fileExts[jamcrc("rUnlockScriptDataNative")] = ".uls"
fileExts[jamcrc("rFacialPartsComboNative")] = ".fpc"
fileExts[jamcrc("rFacialPartsControl")] = ".fpctl"
fileExts[jamcrc("rObjectModelAttachGroupNative")] = ".omg"
fileExts[jamcrc("rObjectModelAttachInfoNative")] = ".omi"
fileExts[jamcrc("rObjectModelAttachSetData")] = ".omas"
fileExts[jamcrc("rMonsterLookAtParamNative")] = ".mlka"
fileExts[jamcrc("rKizunaStoneOfsNative")] = ".kofb"
fileExts[jamcrc("rWeaponKindOfsNative")] = ".wko"
fileExts[jamcrc("uSceneCapture::rCaptureTexture")] = ".tex"
fileExts[jamcrc("cInstancingResource")] = ".ext"
fileExts[jamcrc("rCheatCheckTableAccSkillNative")] = ".cctas"
fileExts[jamcrc("rCheatCheckTableArmorNative")] = ".ccta"
fileExts[jamcrc("rCheatCheckTableBuddyNative")] = ".cctb"
fileExts[jamcrc("rCheatCheckTableBuddyFlagNative")] = ".cctbf"
fileExts[jamcrc("rCheatCheckTableGeneNative")] = ".cctg"
fileExts[jamcrc("rCheatCheckTableNaviAccNative")] = ".cctna"
fileExts[jamcrc("rCheatCheckTableRangeNative")] = ".cctr"
fileExts[jamcrc("rCheatCheckTableWeaponHamNative")] = ".ccthm"
fileExts[jamcrc("rCheatCheckTableWeaponHueNative")] = ".ccthu"
fileExts[jamcrc("rCheatCheckTableWeaponOneNative")] = ".cctwo"
fileExts[jamcrc("rCheatCheckTableWeaponTwoNative")] = ".cctwt"
fileExts[jamcrc("rBattleArenaDLCTableNative")] = ".badt"
fileExts[jamcrc("rBattleArenaTrialTableNative")] = ".batt"
fileExts[jamcrc("rBattleNaviTextEventNative")] = ".bte"
fileExts[jamcrc("rBattleStatusEffectNative")] = ".bseff"
fileExts[jamcrc("rBattleVsPorchPresetNative")] = ".bvspp"
fileExts[jamcrc("rDLCItemTableNative")] = ".ditemp"
fileExts[jamcrc("rDLCRegionTnmntTableNative")] = ".dtnmt"
fileExts[jamcrc("rDLCSubQuestDataNative")] = ".dsuqd"
fileExts[jamcrc("rDLCVsRuleTableNative")] = ".dvsrule"
fileExts[jamcrc("rEnemyCameraParamNative")] = ".ecpd"
fileExts[jamcrc("rLimitedShopDataNative")] = ".lshpd"
fileExts[jamcrc("rLimitedShopPlaceDataNative")] = ".lshppd"
fileExts[jamcrc("rLinkPrizeDataNative")] = ".lpd"
fileExts[jamcrc("rMedalCompRewardNative")] = ".mcr"
fileExts[jamcrc("rMonsterEnumConversionTableNative")] = ".mectd"
fileExts[jamcrc("rNavirouAccessoryDataNative")] = ".nad"
fileExts[jamcrc("rNestEggReviewANative")] = ".nstera"
fileExts[jamcrc("rNestEggReviewBNative")] = ".nsterb"
fileExts[jamcrc("rNestMessageNative")] = ".nstmsg"
fileExts[jamcrc("rOtomonCameraParamNative")] = ".ocpd"
fileExts[jamcrc("rPostmanRewardDataNative")] = ".pmrd"
fileExts[jamcrc("rStaffRollCutDataNative")] = ".srcd"
fileExts[jamcrc("rWorldMapMaskDataNative")] = ".wmmd"
fileExts[jamcrc("rTalkDemoViewSpriteDataNative")] = ".tdvs"
fileExts[jamcrc("rArmorParamNative")] = ".arp"
fileExts[jamcrc("rDLCTableNative")] = ".dlc"
fileExts[jamcrc("rMedalDataListNative")] = ".mdl"
fileExts[jamcrc("rMyhouseBoxCameraDataNative")] = ".mbcd"
fileExts[jamcrc("rStoryTalkBalloonNative")] = ".stb"
fileExts[jamcrc("rWeaponParamNative")] = ".wpp"
fileExts[jamcrc("rBattleEnemyFileNative")] = ".bef"
fileExts[jamcrc("rConditionPriorityDataNative")] = ".cndp"
fileExts[jamcrc("rGatherLevelTableNative")] = ".ghlt"
fileExts[jamcrc("rLimitedShopNpcList")] = ".lsnl"
fileExts[jamcrc("rMonsterBookDataNative")] = ".mbd"
fileExts[jamcrc("rPresetParamNative")] = ".tpp"
fileExts[jamcrc("rPresetParamEquipNative")] = ".tppe"
fileExts[jamcrc("rPresetParamItemNative")] = ".tppi"
fileExts[jamcrc("rPresetParamPlayerNative")] = ".tppp"
fileExts[jamcrc("rSkillFlagNative")] = ".skf"
fileExts[jamcrc("rAppMovie")] = ".dat"
fileExts[jamcrc("rAppMovieIntermediate")] = ".wmv"
fileExts[jamcrc("rCardPose")] = ".cps"
fileExts[jamcrc("rRideParamNative")] = ".rdp"
fileExts[jamcrc("rSequenceCameraList")] = ".scl"
fileExts[jamcrc("rResourceNameForDevNative")] = ".rnmd"
fileExts[jamcrc("rChestItemTableDataNative")] = ".cfid"
fileExts[jamcrc("rGatherSetTableDataNative")] = ".gstd"
fileExts[jamcrc("rFldPlParam_ARNative")] = ".fppar"
fileExts[jamcrc("rFldPlParam_GRNative")] = ".fppgr"
fileExts[jamcrc("rFldPlParam_NRNative")] = ".fppnr"
fileExts[jamcrc("rFldPlParam_WRNative")] = ".fppwr"
fileExts[jamcrc("rAccessoryDataNative")] = ".acd"
fileExts[jamcrc("rAccessoryRareNative")] = ".acr"
fileExts[jamcrc("rAccessorySkillNative")] = ".acs"
fileExts[jamcrc("rArmorDataNative")] = ".ard"
fileExts[jamcrc("rBattleArenaTableNative")] = ".bat"
fileExts[jamcrc("rBattleCommonResourceNative")] = ".bcmr"
fileExts[jamcrc("rBattleEnemySetNative")] = ".bes"
fileExts[jamcrc("rBattleEnemyTblNative")] = ".bemt"
fileExts[jamcrc("rBattleEnemyTblPlanNative")] = ".bemtp"
fileExts[jamcrc("rBattleNpcTblNative")] = ".bnt"
fileExts[jamcrc("rBattlePlayerTblNative")] = ".bplt"
fileExts[jamcrc("rBattleResultBonusNative")] = ".brsb"
fileExts[jamcrc("rBattleStageResourceNative")] = ".bstr"
fileExts[jamcrc("rBattleWeaponTblNative")] = ".bwpt"
fileExts[jamcrc("rBroilerFlavorDataNative")] = ".bfd"
fileExts[jamcrc("rBuddyPathDataNative")] = ".bdypa"
fileExts[jamcrc("rBuddyPlanDataNative")] = ".bdypl"
fileExts[jamcrc("rCallingEncountDataNative")] = ".sce"
fileExts[jamcrc("rConditionNameDataNative")] = ".cnd"
fileExts[jamcrc("rDemoDataNative")] = ".dmd"
fileExts[jamcrc("rDemoFlagDataNative")] = ".dfd"
fileExts[jamcrc("rEggBaseColorDataNative")] = ".ebc"
fileExts[jamcrc("rEncntEnemyPartyNative")] = ".eepd"
fileExts[jamcrc("rEquiprShopDataNative")] = ".eshd"
fileExts[jamcrc("rFieldAISetActNative")] = ".fasa"
fileExts[jamcrc("rFieldAISetKindNative")] = ".fask"
fileExts[jamcrc("rFieldEnemyPathDataNative")] = ".fedpa"
fileExts[jamcrc("rFieldEnemyPlanDataNative")] = ".fedpl"
fileExts[jamcrc("rFieldHuntingDataNative")] = ".fhd"
fileExts[jamcrc("rFieldMotionPackageDataNative")] = ".fmpd"
fileExts[jamcrc("rFieldNpcMotionNative")] = ".fnmd"
fileExts[jamcrc("rFieldPlayerMotionDataNative")] = ".fpm"
fileExts[jamcrc("rFieldSetFlagDataNative")] = ".fsfd"
fileExts[jamcrc("rFurattoFieldDataNative")] = ".fofd"
fileExts[jamcrc("rFurattoTrendDataNative")] = ".fotd"
fileExts[jamcrc("rGalleryFlagDataNative")] = ".gfd"
fileExts[jamcrc("rGatherCommentDataNative")] = ".gcd"
fileExts[jamcrc("rGeneEditNative")] = ".ged"
fileExts[jamcrc("rGeneLottingNative")] = ".glt"
fileExts[jamcrc("rGeneralCountDataNative")] = ".gcd"
fileExts[jamcrc("rGeneralFlagDataNative")] = ".gfd"
fileExts[jamcrc("rGeneTableNative")] = ".gtb"
fileExts[jamcrc("rItemDataNative")] = ".itm"
fileExts[jamcrc("rItemMixNative")] = ".mix"
fileExts[jamcrc("rMainQuestDataNative")] = ".mqsd"
fileExts[jamcrc("rMapMarkerNative")] = ".mmk"
fileExts[jamcrc("rMarkerDataNative")] = ".mkr"
fileExts[jamcrc("rMaterialDataNative")] = ".matd"
fileExts[jamcrc("rMergeStreamDataNative")] = ".asd"
fileExts[jamcrc("rMixFlagNative")] = ".mxf"
fileExts[jamcrc("rMonsterRankTableNative")] = ".mrt"
fileExts[jamcrc("rNekoTaxiStationDataNative")] = ".nsd"
fileExts[jamcrc("rNestHappeningNative")] = ".nhap"
fileExts[jamcrc("rNestHappeningProbNative")] = ".nhapp"
fileExts[jamcrc("rNpcAirouSetResourceLogDataNative")] = ".nasl"
fileExts[jamcrc("rNpcSetResourceLogDataNative")] = ".npsl"
fileExts[jamcrc("rReactionCommentDataNative")] = ".rcd"
fileExts[jamcrc("rRiderNoteDataNative")] = ".rnd"
fileExts[jamcrc("rRiderNoteLargeCategoryDataNative")] = ".rnld"
fileExts[jamcrc("rRiderNotePageDataNative")] = ".rnpd"
fileExts[jamcrc("rRiderNoteSmallCategoryDataNative")] = ".rnsd"
fileExts[jamcrc("rRiderNoteThumbnailDataNative")] = ".rntd"
fileExts[jamcrc("rShortDemoDataNative")] = ".sdm"
fileExts[jamcrc("rSkillTableNative")] = ".skt"
fileExts[jamcrc("rStChapDataNative")] = ".schd"
fileExts[jamcrc("rStEpiDataNative")] = ".sed"
fileExts[jamcrc("rStoryCountDataNative")] = ".scod"
fileExts[jamcrc("rStoryDataNative")] = ".std"
fileExts[jamcrc("rStoryFlagDataNative")] = ".stfd"
fileExts[jamcrc("rStPrComDataNative")] = ".spcd"
fileExts[jamcrc("rSubQuestCountDataNative")] = ".sqcd"
fileExts[jamcrc("rSubQuestFlagDataNative")] = ".sqfd"
fileExts[jamcrc("rSubStEpiDataNative")] = ".ssed"
fileExts[jamcrc("rSystemCountDataNative")] = ".sycd"
fileExts[jamcrc("rTalkDemoActorDataNative")] = ".tdmact"
fileExts[jamcrc("rTalkDemoCommandDataNative")] = ".tdmcmd"
fileExts[jamcrc("rTalkDemoDataNative")] = ".tdmd"
fileExts[jamcrc("rTalkDemoEffectDataNative")] = ".tdmeff"
fileExts[jamcrc("rTalkDemoFaceDataNative")] = ".tdmfc"
fileExts[jamcrc("rTalkDemoMotionDataNative")] = ".tdmmot"
fileExts[jamcrc("rTalkDemoPoseDataNative")] = ".tdmpos"
fileExts[jamcrc("rTalkDemoScript")] = ".tdms"
fileExts[jamcrc("rTalkInfoDataNative")] = ".tid"
fileExts[jamcrc("rTalkMsgDataNative")] = ".tmd"
fileExts[jamcrc("rTalkSelectDataNative")] = ".tstd"
fileExts[jamcrc("rWeaponDataNative")] = ".wpd"
fileExts[jamcrc("rFieldGateDataNative")] = ".fgd"
fileExts[jamcrc("rMHFSMList")] = ".fslm"
fileExts[jamcrc("rWipeData")] = ".wpdt"
fileExts[jamcrc("rBattleAtkNative")] = ".btat"
fileExts[jamcrc("rFieldBuddyMotionDataNative")] = ".fbd"
fileExts[jamcrc("rFieldDataNative")] = ".fld"
fileExts[jamcrc("rFieldEnemySetDataNative")] = ".fesd"
fileExts[jamcrc("rFieldIngredientSetDataNative")] = ".fisd"
fileExts[jamcrc("rFieldMotionDataNative")] = ".fmd"
fileExts[jamcrc("rFieldOrnamentSetDataNative")] = ".fosd"
fileExts[jamcrc("rFieldPredatorDataNative")] = ".fprd"
fileExts[jamcrc("rFieldSchedulerSetDataNative")] = ".fssd"
fileExts[jamcrc("rMonsterRaceDataNative")] = ".mrd"
fileExts[jamcrc("rNpcTalkNative")] = ".ntk"
fileExts[jamcrc("rShopDataNative")] = ".shp"
fileExts[jamcrc("rSystemFlagDataNative")] = ".sfd"
fileExts[jamcrc("rTalkDataNative")] = ".tlk"
fileExts[jamcrc("rProofEffectColorControl")] = ".pec"
fileExts[jamcrc("rProofEffectList")] = ".pel"
fileExts[jamcrc("rProofEffectMotSequenceList")] = ".psl"
fileExts[jamcrc("rProofEffectParamScript")] = ".pep"
fileExts[jamcrc("rCameraData")] = ".cmdt"
fileExts[jamcrc("rColorLinkColor")] = ".clc"
fileExts[jamcrc("rColorLinkInfo")] = ".cli"
fileExts[jamcrc("rConditionChangeInfo")] = ".ccinfo"
fileExts[jamcrc("rDollPartsDisp")] = ".dpd"
fileExts[jamcrc("rGroundAdjustment")] = ".gar"
fileExts[jamcrc("rModelEasyAnime")] = ".mea"
fileExts[jamcrc("rModelInPath")] = ".mip"
fileExts[jamcrc("rMonsterPartsDisp")] = ".mpd"
fileExts[jamcrc("rNavirouPartsDisp")] = ".npd"
fileExts[jamcrc("rPartsVisibleInfo")] = ".pvi"
fileExts[jamcrc("rSchedulerPreLoadList")] = ".spll"
fileExts[jamcrc("rShadowParamNative")] = ".swp"
fileExts[jamcrc("rVirtualJoint")] = ".vjr"
fileExts[jamcrc("rWeaponGimmickInfo")] = ".wgi"
fileExts[jamcrc("rWeaponOfsForBodyNative")] = ".wofb"
fileExts[jamcrc("cResource")] = ".ext"
fileExts[jamcrc("rModel")] = ".mod"
fileExts[jamcrc("rMotionList")] = ".lmt"
fileExts[jamcrc("rTexture")] = ".tex"
fileExts[jamcrc("rCollision")] = ".sbc"
fileExts[jamcrc("rAIWayPointGraph")] = ".gway"
fileExts[jamcrc("rScheduler")] = ".sdl"
fileExts[jamcrc("rArchive")] = ".arc"
fileExts[jamcrc("rCnsTinyChain")] = ".ctc"
fileExts[jamcrc("rChain")] = ".chn"
fileExts[jamcrc("rChainCol")] = ".ccl"
fileExts[jamcrc("rAIFSM")] = ".fsm"
fileExts[jamcrc("rAIFSMList")] = ".fsl"
fileExts[jamcrc("rAIConditionTree")] = ".cdt"
fileExts[jamcrc("rCameraList")] = ".lcm"
fileExts[jamcrc("rGUI")] = ".gui"
fileExts[jamcrc("rRenderTargetTexture")] = ".rtex"
fileExts[jamcrc("rEffect2D")] = ".e2d"
fileExts[jamcrc("rGUIFont")] = ".gfd"
fileExts[jamcrc("rGUIIconInfo")] = ".gii"
fileExts[jamcrc("rGUIStyle")] = ".gst"
fileExts[jamcrc("rGUIMessage")] = ".gmd"
fileExts[jamcrc("rDeformWeightMap")] = ".dwm"
fileExts[jamcrc("rSwingModel")] = ".swm"
fileExts[jamcrc("rVibration")] = ".vib"
fileExts[jamcrc("rSoundRequest")] = ".srqr"
fileExts[jamcrc("rSoundStreamRequest")] = ".stqr"
fileExts[jamcrc("rSoundCurveSet")] = ".scsr"
fileExts[jamcrc("rSoundDirectionalSet")] = ".sdsr"
fileExts[jamcrc("rSoundEQ")] = ".equr"
fileExts[jamcrc("rSoundReverb")] = ".revr"
fileExts[jamcrc("rSoundCurveXml")] = ".scvr.xml"
fileExts[jamcrc("rSoundDirectionalCurveXml")] = ".sdcr.xml"
fileExts[jamcrc("rSoundBank")] = ".sbkr"
fileExts[jamcrc("rSoundPhysicsRigidBody")] = ".sprr"
fileExts[jamcrc("rSoundPhysicsSoftBody")] = ".spsr"
fileExts[jamcrc("rSoundPhysicsJoint")] = ".spjr"
fileExts[jamcrc("rShader2")] = ".mfx"
fileExts[jamcrc("rImplicitSurface")] = ".is"
fileExts[jamcrc("rMovie")] = ".ext"
fileExts[jamcrc("rMovieOnMemory")] = ".mem.wmv"
fileExts[jamcrc("rMovieOnDisk")] = ".wmvd"
fileExts[jamcrc("rMovieOnMemoryInterMediate")] = ".mem.wmv"
fileExts[jamcrc("rMovieOnDiskInterMediate")] = ".wmvd"
fileExts[jamcrc("rSceneTexture")] = ".stex"
fileExts[jamcrc("rGrass2")] = ".gr2"
fileExts[jamcrc("rGrass2Setting")] = ".gr2s"
fileExts[jamcrc("rOccluder")] = ".occ"
fileExts[jamcrc("rISC")] = ".isc"
fileExts[jamcrc("rSky")] = ".sky"
fileExts[jamcrc("rStarCatalog")] = ".stc"
fileExts[jamcrc("rCloud")] = ".cld"
fileExts[jamcrc("rSoundSourcePC")] = ".ext"
fileExts[jamcrc("rSoundSourceMSADPCM")] = ".xsew"
fileExts[jamcrc("rSoundSourceOggVorbis")] = ".sngw"
fileExts[jamcrc("rEffectList")] = ".efl"
fileExts[jamcrc("rCollisionHeightField")] = ".sbch"
fileExts[jamcrc("rCnsIK")] = ".ik"
fileExts[jamcrc("rShaderPackage")] = ".spkg"
fileExts[jamcrc("rShaderCache")] = ".sch"
fileExts[jamcrc("rMaterial")] = ".mrl"
fileExts[jamcrc("rSoundSpeakerSetXml")] = ".sssr.xml"
fileExts[jamcrc("rCollisionObj")] = ".obc"
fileExts[jamcrc("rGrass")] = ".grs"
fileExts[jamcrc("rConstraint")] = ".ext"
fileExts[jamcrc("rCnsLookAt")] = ".lat"
fileExts[jamcrc("rEffectAnim")] = ".ean"
fileExts[jamcrc("rEffectStrip")] = ".efs"
fileExts[jamcrc("rVertices")] = ".vts"
fileExts[jamcrc("rNulls")] = ".nls"
fileExts[jamcrc("rAI")] = ".ais"
fileExts[jamcrc("rSoundPhysicsList")] = ".splr"
fileExts[jamcrc("rFacialAnimation")] = ".fca"
fileExts[jamcrc("rMetaSet")] = ".mst"
fileExts[jamcrc("rMetaSetXml")] = ".mst.xml"
fileExts[jamcrc("rCnsTinyIK")] = ".tik"
fileExts[jamcrc("rCnsScaleNormalize")] = ".scnl"
fileExts[jamcrc("rCnsRotateLimit")] = ".lim"
fileExts[jamcrc("rCnsMatrix")] = ".mtx"
fileExts[jamcrc("rCnsJointOffset")] = ".jof"
fileExts[jamcrc("rCnsParent")] = ".par"
fileExts[jamcrc("rCnsParentN")] = ".pan"
fileExts[jamcrc("rCnsLookAtEyeball")] = ".eye"
fileExts[jamcrc("rGraphPatch")] = ".gpt"
fileExts[jamcrc("rGrassWind")] = ".grw"
fileExts[jamcrc("rConvexHull")] = ".hul"
fileExts[jamcrc("rGeometry2")] = ".geo2"
fileExts[jamcrc("rGeometry3")] = ".geo3"
fileExts[jamcrc("rSerial")] = ".srt"
fileExts[jamcrc("rDynamicSbc")] = ".dsc"
fileExts[jamcrc("rGeometry2Group")] = ".geog"

class Reader():
    def __init__(self, data):
        self.offset = 0
        self.data = data
        self.partial_offset = 0
        self.partial_data = None

    def read(self, kind, size):
        result = struct.unpack(kind, self.data[self.offset:self.offset+size])[0]
        self.offset += size
        return result

    def seek(self, offset, start = None):
        if start is None:
            self.offset = offset
        else:
            self.offset += offset

    def readUInt(self):
        return self.read("I", 4)

    def readInt(self):
        return self.read("i", 4)

    def readUInt64(self):
        return self.read("Q", 8)

    def readHalf(self):
        return self.read("e", 2)

    def readFloat(self):
        return self.read("f", 4)

    def readShort(self):
        return self.read("h", 2)

    def readUShort(self):
        return self.read("H", 2)

    def readByte(self):
        return self.read("b", 1)

    def readBytes(self, size):
        return self.data[self.offset:self.offset + size]

    # this function will definitelly stop working if you look at it too hard
    def readBytes_unpackbin(self, bits, block_size, signed=False):
        value = 0
        remaining_bits = bits
        movement = min(remaining_bits, block_size)
        while True:
            if self.partial_offset == 0:
                if block_size == 8:
                    self.partial_data = self.readUByte()
                elif block_size == 16:
                    self.partial_data = self.readUShort()
                elif block_size == 32:
                    self.partial_data = self.readUInt()
                elif block_size == 64:
                    self.partial_data = self.readUInt64()
            movement = min(remaining_bits, block_size-self.partial_offset)
            value = value << movement
            value = value | (self.partial_data & ((2**movement)-1))
            self.partial_data = self.partial_data >> movement
            remaining_bits -= movement
            self.partial_offset = (self.partial_offset + movement)%block_size
            movement = min(remaining_bits, block_size)

            if remaining_bits == 0:
                if signed == True:
                    maxval = ((1 << bits) - 1)
                    if value > (maxval >> 1):
                        value -= maxval
                    value = value / (maxval >> 1)
                return value

    def readBytes_to_int(self, size):
        self.readUByte()
        value = int.from_bytes(self.readBytes(size), byteorder='little')
        self.offset += size
        return value

    def readUByte(self):
        return self.read("B", 1)

    def readString(self):
        text = ""
        while True:
            char = self.readUByte()
            if char == 0:
                break
            else:
                text += chr(char)
        return text

    def readStringUTFAt(self, offset):
        previous_offset = self.tell()
        self.seek(offset)
        text = ""
        while True:
            char = self.readUShort()
            if char == 0:
                break
            else:
                text += chr(char)
        self.seek(previous_offset)
        return text

    def readStringUTF(self):
        text = ""
        while True:
            char = self.readUShort()
            if char == 0:
                break
            else:
                text += chr(char)
        return text

    def allign(self, size):
        self.offset = (int((self.offset)/size)*size)+size

    def tell(self):
        return self.offset

    def getSize(self):
        return len(self.data)

def SetLoggingLevel(level):
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)
    elif level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif level == "ERROR":
        logger.setLevel(logging.ERROR)

def bulk_extract_arc(context):

    candidate_modules = [mod for mod in addon_utils.modules() if mod.bl_info["name"] == "MH Stories 2 tool suite"]
    if len(candidate_modules) > 1:
        logger.warning("Inconsistencies while loading the addon preferences: make sure you don't have multiple versions of the addon installed.")
    mod = candidate_modules[0]
    addon_prefs = context.preferences.addons[mod.__name__].preferences
    SetLoggingLevel(addon_prefs.logging_level)

    shared_library_path = None
    shared_library_filename = "blowfish.so"
    if sys.platform == "linux" or sys.platform == "linux2":
        shared_library_filename = "blowfish.so"
    elif sys.platform == "win32":
        shared_library_filename = "blowfish.dll"

    shared_library_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), shared_library_filename)

    lib = ctypes.cdll.LoadLibrary(shared_library_path)
    lib.decrypt_arc.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
    lib.decrypt_arc.restype = ctypes.c_int

    extraction_path = addon_prefs.game_path
    if extraction_path == "":
        logger.error("Fill the game path before starting the ARC file extraction")
        return

    if not os.path.isdir(extraction_path):
        logger.error("Unable to access folder " + str(extraction_path))
        return

    if addon_prefs.installation_game_path == "":
        installation_path = extraction_path
    else:
        if not os.path.isdir(addon_prefs.installation_game_path):
            logger.error("Unable to access folder " + str(addon_prefs.installation_game_path))
            return
        installation_path = addon_prefs.installation_game_path


    arc_files = glob(os.path.join(installation_path, "**", "*.arc"), recursive=True)
    logger.info("Found " + str(len(arc_files)) + " arc files.")

    extracted_file_count = 0
    file_list = set()
    for arc_file_i, arc_file in enumerate(arc_files):
        with open(arc_file, "rb") as file_in:
            data = file_in.read()
        arc_bs = Reader(data)
        magic = arc_bs.readUInt()
        _ = arc_bs.readUShort()
        file_count = arc_bs.readUShort()
        if magic == 1128485441:
            # Encrypted arc
            ebs = Reader(arc_bs.data[arc_bs.offset:])
            key = b"QZHaM;-5:)dV#"
            ret = lib.decrypt_arc(
                np.frombuffer(ebs.data, np.uint8).ctypes.data_as(ctypes.c_void_p),
                len(ebs.data),
                np.frombuffer(key, np.uint8).ctypes.data_as(ctypes.c_void_p),
                len(key)
            )
            bs = Reader(ebs.data)

        elif magic == b"ARC\x00":
            # Regular arc
            bs = Reader(arc_bs.data[bs.offset:])
        else:
            logger.warning("File " + arc_file + " is not an recognized ARC file. ")
            continue

        file_infos = []

        for file_i in range(file_count):
            file_info = {}
            starting_point = bs.tell()
            file_info["file_path"] = bs.readString().replace("\\", "/")
            bs.seek(starting_point + 128)
            extension_hash = bs.readUInt()
            if extension_hash in fileExts.keys():
                file_info["extension"] = fileExts[extension_hash]
            file_info["compressed_size"] = bs.readUInt()
            file_info["decompressed_size"] = bs.readUInt()
            file_info["offset"] = bs.readUInt() - 8 # because the header isn't included
            if extension_hash not in fileExts.keys():
                continue
            file_infos.append(file_info)

        for file_info in file_infos:
            file_list.add((file_info["file_path"] + file_info["extension"]).replace("\\", "/"))
            output_name = os.path.join(extraction_path, file_info["file_path"] + file_info["extension"])
            if os.path.exists(output_name):
                pass
            else:
                bs.seek(file_info["offset"])
                compressed_bytes = bs.readBytes(file_info["compressed_size"])
                decompressed_bytes = zlib.decompress(compressed_bytes)

                try:
                    os.makedirs(os.path.dirname(output_name))
                except FileExistsError as e:
                    pass
                with open(output_name, "wb") as file_out:
                    file_out.write(decompressed_bytes)

        if extracted_file_count%50 == 0:
            logger.info(str(extracted_file_count) + "/" + str(len(arc_files)) + " arc files extracted")
        extracted_file_count += 1

    logger.info(str(extracted_file_count) + " arc files extracted.")

    
    if extraction_path != installation_path:
        extracted_file_count = 0

        other_files = []
        for x in glob(os.path.join(installation_path, "nativeDX11x64", "**", "*"), recursive=True):
            if "." + x.split(".")[-1] in fileExts.values() and x.split(".")[-1] != "arc":
                other_files.append(x)
        logger.info("Found " + str(len(other_files)) + " other files.")

        for other_file in other_files:
            file_list.add(other_file[other_file.find("nativeDX11x64") + len("nativeDX11x64")+1:].replace("\\", "/"))
            dest_path = os.path.join(extraction_path, other_file[other_file.find("nativeDX11x64") + len("nativeDX11x64")+1:])
            if os.path.exists(dest_path):
                pass
            else:
                try:
                    os.makedirs(os.path.dirname(dest_path))
                except FileExistsError as e:
                    pass
                shutil.copy(other_file, dest_path)
            if extracted_file_count%50 == 0:
                logger.info(str(extracted_file_count) + "/" + str(len(other_files)) + " other files extracted")
            extracted_file_count += 1

    file_list = sorted(list(file_list))
    with open(os.path.join(extraction_path, "file_list.json"), "w") as json_out:
        json.dump(file_list, json_out, indent="\t")
    if sys.platform == "win32":
        dll_close = ctypes.windll.kernel32.FreeLibrary
        dll_close.argtypes = [ctypes.c_void_p]
        dll_close(lib._handle)
