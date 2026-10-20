# Полный реверс-инжиниринг реального приложения YAZIO (из APK + UI Dumps)

- **Источник:** Установленный пакет `com.yazio.android` (`base.apk`, 61.5 МБ) с эмулятора `emulator-5554`
- **Найдено основных классов `yazio/*` (без внутренних `$`):** 920
- **Проанализировано XML UI-дампов экранов:** 43

## 1. Точная SQL-схема локальной базы данных YAZIO (из DEX байткода)

```sql
CREATE TABLE CachedUserProperty ( id INTEGER PRIMARY KEY AUTOINCREMENT, insertedAt INTEGER NOT NULL, type INTEGER NOT NULL, proto BLOB NOT NULL, UNIQUE(insertedAt, type) );

CREATE TABLE IF NOT EXISTS `_new_user` (`heightUnit` TEXT NOT NULL, `language` TEXT NOT NULL, `startWeightKg` REAL NOT NULL, `heightInCm` REAL NOT NULL, `birthDate` TEXT NOT NULL, `gender` TEXT NOT NULL, `mail` TEXT NOT NULL, `firstName` TEXT NOT NULL, `lastName` TEXT NOT NULL, `city` TEXT NOT NULL, `weightUnit` TEXT NOT NULL, `weightChangePerWeek` REAL NOT NULL, `energyUnit` TEXT NOT NULL, `servingUnit` TEXT NOT NULL, `registration` TEXT NOT NULL, `diet` TEXT NOT NULL, `glucoseUnit` TEXT NOT NULL, `profileImage` TEXT, `userToken` TEXT NOT NULL, `emailConfirmationStatus` TEXT NOT NULL, `timezoneOffset` INTEGER NOT NULL, `loginType` TEXT NOT NULL, `pal` REAL NOT NULL, `lastActive` TEXT, `newsLetterOptIn` INTEGER, `id` INTEGER NOT NULL, `uuid` TEXT NOT NULL, `premiumType` TEXT, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `_new_user` (`heightUnit` TEXT NOT NULL, `startWeightKg` REAL NOT NULL, `heightInCm` REAL NOT NULL, `birthDate` TEXT NOT NULL, `gender` TEXT NOT NULL, `mail` TEXT NOT NULL, `firstName` TEXT NOT NULL, `lastName` TEXT NOT NULL, `city` TEXT NOT NULL, `weightUnit` TEXT NOT NULL, `weightChangePerWeek` REAL NOT NULL, `energyUnit` TEXT NOT NULL, `servingUnit` TEXT NOT NULL, `registration` TEXT NOT NULL, `diet` TEXT NOT NULL, `glucoseUnit` TEXT NOT NULL, `profileImage` TEXT, `userToken` TEXT NOT NULL, `emailConfirmationStatus` TEXT NOT NULL, `timezoneOffset` INTEGER NOT NULL, `loginType` TEXT NOT NULL, `newsLetterOptIn` INTEGER, `id` INTEGER NOT NULL, `uuid` TEXT NOT NULL, `premiumType` TEXT, `activityDegree` TEXT NOT NULL, `foodDatabaseCountry` TEXT DEFAULT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `activeChallenge` (`challenge` TEXT NOT NULL, `startedAt` INTEGER NOT NULL, `id` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `beforeAfterSettings` (`background` TEXT NOT NULL, `font` TEXT, `layout` TEXT NOT NULL, `title` TEXT, `startWeightKg` REAL, `currentWeightKg` REAL, `startDate` TEXT, `currentDate` TEXT, `selectedInputs` TEXT, `id` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `customTraining` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `epochMillis` INTEGER NOT NULL, `name` TEXT NOT NULL, `caloriesBurned` REAL NOT NULL, `durationInMinutes` INTEGER NOT NULL);

CREATE TABLE IF NOT EXISTS `doneFoodPlans` (`foodPlan` TEXT NOT NULL, PRIMARY KEY(`foodPlan`));

CREATE TABLE IF NOT EXISTS `fastingPlan` (`type` TEXT NOT NULL, `startDate` TEXT NOT NULL, `startEatingAt` TEXT NOT NULL, `id` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `foodPlanDays` (`completed` INTEGER NOT NULL, `doneTasks` TEXT NOT NULL, `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL);

CREATE TABLE IF NOT EXISTS `foodPlanDays` (`completed` INTEGER NOT NULL, `doneTasks` TEXT NOT NULL, `liked` INTEGER NOT NULL, `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL);

CREATE TABLE IF NOT EXISTS `foodPlanMetaData` (`startDate` TEXT NOT NULL, `foodPlan` TEXT NOT NULL, `manuallyEnded` INTEGER NOT NULL, `id` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `foodRatingTable` (`uuid` TEXT NOT NULL, PRIMARY KEY(`uuid`));

CREATE TABLE IF NOT EXISTS `groceryInfo` (`name` TEXT NOT NULL, `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL);

CREATE TABLE IF NOT EXISTS `groceryIngredient` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `name` TEXT NOT NULL, `done` INTEGER NOT NULL, `infoId` INTEGER NOT NULL, FOREIGN KEY(`infoId`) REFERENCES `groceryInfo`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE );

CREATE TABLE IF NOT EXISTS `groceryList` ( `recipeId` TEXT NOT NULL, `portionCount` REAL NOT NULL, `boughtServings` TEXT NOT NULL, `deletedServings` TEXT NOT NULL, `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL );

CREATE TABLE IF NOT EXISTS `groceryList` (`recipeId` TEXT NOT NULL, `portionCount` REAL NOT NULL, `boughtServings` TEXT NOT NULL, `deletedServings` TEXT NOT NULL, `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL);

CREATE TABLE IF NOT EXISTS `lastTrainingInsertion` (`epochMillis` INTEGER NOT NULL, `trainingName` TEXT NOT NULL, `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL);

CREATE TABLE IF NOT EXISTS `pendingFeeling` (`date` TEXT NOT NULL, `note` TEXT, `tagsAdded` TEXT NOT NULL, `tagsRemoved` TEXT NOT NULL, PRIMARY KEY(`date`));

CREATE TABLE IF NOT EXISTS `pendingWaterIntake` (`dateTime` TEXT NOT NULL, `intake` REAL NOT NULL, `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL);

CREATE TABLE IF NOT EXISTS `pendingWaterIntake` (`date` TEXT NOT NULL, `water_intake` REAL NOT NULL, `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL);

CREATE TABLE IF NOT EXISTS `pendingWeightInsert` (`kilogram` REAL NOT NULL, `date` TEXT NOT NULL, PRIMARY KEY(`date`));

CREATE TABLE IF NOT EXISTS `podcastPosition` (`positionMs` INTEGER NOT NULL, `path` TEXT NOT NULL, PRIMARY KEY(`path`));

CREATE TABLE IF NOT EXISTS `recipeSearchMetaData` (`language` TEXT NOT NULL, `insertedAt` TEXT NOT NULL, PRIMARY KEY(`language`));

CREATE TABLE IF NOT EXISTS `recipeSearch` (`id` TEXT NOT NULL, `name` TEXT NOT NULL, `nutrients` TEXT NOT NULL, `imageUrl` TEXT NOT NULL, `portionCount` INTEGER NOT NULL, `tags` TEXT NOT NULL, `availableSince` TEXT NOT NULL, `language` TEXT NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `recipe` (`id` TEXT NOT NULL, `name` TEXT NOT NULL, `isYazioRecipe` INTEGER NOT NULL, `nutrients` TEXT NOT NULL, `minerals` TEXT NOT NULL, `vitamins` TEXT NOT NULL, `imageUrl` TEXT, `portionCount` INTEGER NOT NULL, `servings` TEXT NOT NULL, `description` TEXT, `instructions` TEXT NOT NULL, `tags` TEXT NOT NULL, `preparationTimeInMinutes` INTEGER NOT NULL, `difficulty` TEXT NOT NULL, `isPublic` INTEGER NOT NULL, `fetchedAt` INTEGER NOT NULL, `isFreeRecipe` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `userSettingsPatch` (`accountTrainingEnergy` INTEGER, `showFoodNotification` INTEGER, `showFoodTips` INTEGER, `showRecipeTips` INTEGER, `showTipNotification` INTEGER, `showWaterNotification` INTEGER, `showWeightNotification` INTEGER, `useWaterTracker` INTEGER, `id` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `userSettings` (`showFoodNotification` INTEGER NOT NULL, `showWaterNotification` INTEGER NOT NULL, `showTipNotification` INTEGER NOT NULL, `showRecipeTips` INTEGER NOT NULL, `accountTrainingEnergy` INTEGER NOT NULL, `showWeightNotification` INTEGER NOT NULL, `showFoodTips` INTEGER NOT NULL, `useWaterTracker` INTEGER NOT NULL, `addedAt` INTEGER NOT NULL, `id` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `userTable` ( `heightUnit` TEXT NOT NULL, `language` TEXT NOT NULL, `startWeightKg` REAL NOT NULL, `heightInCm` REAL NOT NULL, `birthDate` TEXT NOT NULL, `gender` TEXT NOT NULL, `isPremium` INTEGER NOT NULL, `mail` TEXT NOT NULL, `firstName` TEXT NOT NULL, `lastName` TEXT NOT NULL, `city` TEXT NOT NULL, `target` TEXT NOT NULL, `weightUnit` TEXT NOT NULL, `weightChangePerWeek` REAL, `activityDegree` TEXT NOT NULL, `energyUnit` TEXT NOT NULL, `servingUnit` TEXT NOT NULL, `registration` TEXT NOT NULL, `foodPlan` TEXT NOT NULL, `glucoseUnit` TEXT NOT NULL, `currentWeight` REAL NOT NULL, `profileImage` TEXT, `id` INTEGER NOT NULL, `user_token` TEXT, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `userTable` (`heightUnit` TEXT NOT NULL, `language` TEXT NOT NULL, `startWeightKg` REAL NOT NULL, `heightInCm` REAL NOT NULL, `birthDate` TEXT NOT NULL, `gender` TEXT NOT NULL, `isPremium` INTEGER NOT NULL, `mail` TEXT NOT NULL, `firstName` TEXT NOT NULL, `lastName` TEXT NOT NULL, `city` TEXT NOT NULL, `target` TEXT NOT NULL, `weightUnit` TEXT NOT NULL, `weightChangePerWeek` REAL, `activityDegree` TEXT NOT NULL, `energyUnit` TEXT NOT NULL, `servingUnit` TEXT NOT NULL, `displayFoodTips` INTEGER NOT NULL, `displayRecipeTips` INTEGER NOT NULL, `registration` TEXT NOT NULL, `foodPlan` TEXT NOT NULL, `glucoseUnit` TEXT NOT NULL, `currentWeight` REAL NOT NULL, `showFoodNotification` INTEGER NOT NULL, `showWeightNotification` INTEGER NOT NULL, `showTipNotification` INTEGER NOT NULL, `showWaterNotification` INTEGER NOT NULL, `useWaterTracker` INTEGER NOT NULL, `profileImage` TEXT, `id` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `userTable` (`heightUnit` TEXT NOT NULL, `language` TEXT NOT NULL, `startWeightKg` REAL NOT NULL, `heightInCm` REAL NOT NULL, `birthDate` TEXT NOT NULL, `gender` TEXT NOT NULL, `isPremium` INTEGER NOT NULL, `mail` TEXT NOT NULL, `firstName` TEXT NOT NULL, `lastName` TEXT NOT NULL, `city` TEXT NOT NULL, `target` TEXT NOT NULL, `weightUnit` TEXT NOT NULL, `weightChangePerWeek` REAL, `activityDegree` TEXT NOT NULL, `energyUnit` TEXT NOT NULL, `servingUnit` TEXT NOT NULL, `registration` TEXT NOT NULL, `foodPlan` TEXT NOT NULL, `glucoseUnit` TEXT NOT NULL, `currentWeight` REAL NOT NULL, `profileImage` TEXT, `id` INTEGER NOT NULL, `user_token` TEXT, `emailConfirmationStatus` TEXT NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `user` (`heightUnit` TEXT NOT NULL, `language` TEXT NOT NULL, `startWeightKg` REAL NOT NULL, `heightInCm` REAL NOT NULL, `birthDate` TEXT NOT NULL, `gender` TEXT NOT NULL, `isPremium` INTEGER NOT NULL, `mail` TEXT NOT NULL, `firstName` TEXT NOT NULL, `lastName` TEXT NOT NULL, `city` TEXT NOT NULL, `weightUnit` TEXT NOT NULL, `weightChangePerWeek` REAL NOT NULL, `energyUnit` TEXT NOT NULL, `servingUnit` TEXT NOT NULL, `registration` TEXT NOT NULL, `diet` TEXT NOT NULL, `glucoseUnit` TEXT NOT NULL, `profileImage` TEXT, `userToken` TEXT NOT NULL, `emailConfirmationStatus` TEXT NOT NULL, `timezoneOffset` INTEGER NOT NULL, `loginType` TEXT NOT NULL, `pal` REAL NOT NULL, `lastActive` TEXT, `newsLetterOptIn` INTEGER, `id` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `user` (`heightUnit` TEXT NOT NULL, `language` TEXT NOT NULL, `startWeightKg` REAL NOT NULL, `heightInCm` REAL NOT NULL, `birthDate` TEXT NOT NULL, `gender` TEXT NOT NULL, `isPremium` INTEGER NOT NULL, `mail` TEXT NOT NULL, `firstName` TEXT NOT NULL, `lastName` TEXT NOT NULL, `city` TEXT NOT NULL, `weightUnit` TEXT NOT NULL, `weightChangePerWeek` REAL NOT NULL, `energyUnit` TEXT NOT NULL, `servingUnit` TEXT NOT NULL, `registration` TEXT NOT NULL, `diet` TEXT NOT NULL, `glucoseUnit` TEXT NOT NULL, `profileImage` TEXT, `userToken` TEXT, `emailConfirmationStatus` TEXT NOT NULL, `timezoneOffset` INTEGER NOT NULL, `loginType` TEXT NOT NULL, `pal` REAL NOT NULL, `id` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `user` (`heightUnit` TEXT NOT NULL, `language` TEXT NOT NULL, `startWeightKg` REAL NOT NULL, `heightInCm` REAL NOT NULL, `birthDate` TEXT NOT NULL, `gender` TEXT NOT NULL, `mail` TEXT NOT NULL, `firstName` TEXT NOT NULL, `lastName` TEXT NOT NULL, `city` TEXT NOT NULL, `weightUnit` TEXT NOT NULL, `weightChangePerWeek` REAL NOT NULL, `energyUnit` TEXT NOT NULL, `servingUnit` TEXT NOT NULL, `registration` TEXT NOT NULL, `diet` TEXT NOT NULL, `glucoseUnit` TEXT NOT NULL, `profileImage` TEXT, `userToken` TEXT NOT NULL, `emailConfirmationStatus` TEXT NOT NULL, `timezoneOffset` INTEGER NOT NULL, `loginType` TEXT NOT NULL, `lastActive` TEXT, `newsLetterOptIn` INTEGER, `id` INTEGER NOT NULL, `uuid` TEXT NOT NULL, `premiumType` TEXT, `activityDegree` TEXT NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `user` (`heightUnit` TEXT NOT NULL, `language` TEXT NOT NULL, `startWeightKg` REAL NOT NULL, `heightInCm` REAL NOT NULL, `birthDate` TEXT NOT NULL, `gender` TEXT NOT NULL, `mail` TEXT NOT NULL, `firstName` TEXT NOT NULL, `lastName` TEXT NOT NULL, `city` TEXT NOT NULL, `weightUnit` TEXT NOT NULL, `weightChangePerWeek` REAL NOT NULL, `energyUnit` TEXT NOT NULL, `servingUnit` TEXT NOT NULL, `registration` TEXT NOT NULL, `diet` TEXT NOT NULL, `glucoseUnit` TEXT NOT NULL, `profileImage` TEXT, `userToken` TEXT NOT NULL, `emailConfirmationStatus` TEXT NOT NULL, `timezoneOffset` INTEGER NOT NULL, `loginType` TEXT NOT NULL, `pal` REAL NOT NULL, `lastActive` TEXT, `newsLetterOptIn` INTEGER, `id` INTEGER NOT NULL, `uuid` TEXT, `premiumType` TEXT, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS `user` (`heightUnit` TEXT NOT NULL, `startWeightKg` REAL NOT NULL, `heightInCm` REAL NOT NULL, `birthDate` TEXT NOT NULL, `gender` TEXT NOT NULL, `mail` TEXT NOT NULL, `firstName` TEXT NOT NULL, `lastName` TEXT NOT NULL, `city` TEXT NOT NULL, `weightUnit` TEXT NOT NULL, `weightChangePerWeek` REAL NOT NULL, `energyUnit` TEXT NOT NULL, `servingUnit` TEXT NOT NULL, `registration` TEXT NOT NULL, `diet` TEXT NOT NULL, `glucoseUnit` TEXT NOT NULL, `profileImage` TEXT, `userToken` TEXT NOT NULL, `emailConfirmationStatus` TEXT NOT NULL, `timezoneOffset` INTEGER NOT NULL, `loginType` TEXT NOT NULL, `newsLetterOptIn` INTEGER, `id` INTEGER NOT NULL, `uuid` TEXT NOT NULL, `premiumType` TEXT, `activityDegree` TEXT NOT NULL, `foodDatabaseCountry` TEXT DEFAULT NULL, `reset` INTEGER, `goal` TEXT, `languageCode` TEXT, PRIMARY KEY(`id`));

CREATE TABLE IF NOT EXISTS user_attributes ( app_id TEXT NOT NULL, name TEXT NOT NULL, set_timestamp INTEGER NOT NULL, value BLOB NOT NULL, PRIMARY KEY (app_id, name));

CREATE TABLE UserId ( entryId INTEGER PRIMARY KEY NOT NULL, userId TEXT NOT NULL, CHECK(entryId=0) );

CREATE TABLE `activeChallenge` (`challenge` TEXT NOT NULL, `startedAt` INTEGER NOT NULL, `id` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE `fastingPlan` (`type` TEXT NOT NULL, `startDate` TEXT NOT NULL, `startEatingAt` TEXT NOT NULL, `id` INTEGER NOT NULL, PRIMARY KEY(`id`));

CREATE TABLE `foodRated` (`uuid` TEXT NOT NULL, PRIMARY KEY(`uuid`));

CREATE TABLE `groceryList` (`recipeId` TEXT NOT NULL, `portionCount` REAL NOT NULL, `boughtServings` TEXT NOT NULL, `deletedServings` TEXT NOT NULL, `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL);

CREATE TABLE `lastTrainingInsertion` (`epochMillis` INTEGER NOT NULL, `trainingName` TEXT NOT NULL, `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL);

CREATE TABLE `pendingFeeling` (`date` TEXT NOT NULL, `note` TEXT, `tagsAdded` TEXT NOT NULL, `tagsRemoved` TEXT NOT NULL, PRIMARY KEY(`date`));

CREATE TABLE `pendingWaterIntake` (`dateTime` TEXT NOT NULL, `intake` REAL NOT NULL, `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL);

CREATE TABLE `pendingWeightInsert` (`kilogram` REAL NOT NULL, `date` TEXT NOT NULL, PRIMARY KEY(`date`));

CREATE TABLE `podcastPosition` (`position` INTEGER NOT NULL, `path` TEXT NOT NULL, PRIMARY KEY(`path`));

CREATE TABLE lastSentFcmToken( id INTEGER PRIMARY KEY NOT NULL CHECK(id = 0), fcmToken TEXT NOT NULL, userToken TEXT NOT NULL );

CREATE TABLE likedPodcast ( podcastIndex INTEGER PRIMARY KEY NOT NULL, liked INTEGER NOT NULL );

CREATE TABLE pendingRecipeFavTransaction ( recipeId TEXT PRIMARY KEY NOT NULL, portionCount REAL );

CREATE TABLE pendingWeightInsert( `kilogram` REAL NOT NULL, `date` TEXT NOT NULL, PRIMARY KEY(`date`) );

CREATE TABLE recipe ( id TEXT PRIMARY KEY NOT NULL, yazioId TEXT NOT NULL, name TEXT NOT NULL, description TEXT, difficulty TEXT, isYazioRecipe INTEGER NOT NULL, isFreeRecipe INTEGER NOT NULL, image TEXT, portionCount INTEGER NOT NULL, availableSince TEXT, preparationTimeInMinutes INTEGER, rank INTEGER, locale TEXT NOT NULL, updatedAt INTEGER NOT NULL );

CREATE TABLE recipe ( id TEXT PRIMARY KEY NOT NULL, yazioId TEXT, name TEXT NOT NULL, description TEXT, difficulty TEXT, isYazioRecipe INTEGER NOT NULL, isProRecipe INTEGER NOT NULL, image TEXT, portionCount INTEGER NOT NULL, availableSince TEXT, preparationTimeInMinutes INTEGER, rank REAL, UNIQUE(yazioId) );

CREATE TABLE recipeColor ( recipeId TEXT PRIMARY KEY NOT NULL, color TEXT NOT NULL );

CREATE TABLE recipeDownloadMetadata ( locale TEXT PRIMARY KEY NOT NULL, nextPageLink TEXT, changesIndicator TEXT NOT NULL );

CREATE TABLE recipeInstruction ( recipeId TEXT NOT NULL REFERENCES recipe, instruction TEXT NOT NULL, step INTEGER NOT NULL, PRIMARY KEY (recipeId, step) );

CREATE TABLE recipeInstruction ( recipeId TEXT NOT NULL, instruction TEXT NOT NULL );

CREATE TABLE recipeNutrient ( recipeId TEXT NOT NULL REFERENCES recipe, serverName TEXT NOT NULL, gram REAL NOT NULL, PRIMARY KEY (recipeId, serverName) );

CREATE TABLE recipeNutrient ( recipeId TEXT NOT NULL, serverName TEXT NOT NULL, gram REAL NOT NULL );

CREATE TABLE recipeServing ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, recipeId TEXT NOT NULL REFERENCES recipe, name TEXT NOT NULL, amountOfBaseUnit REAL, serving TEXT, servingQuantity REAL, baseUnit TEXT, note TEXT, productId TEXT, producer TEXT );

CREATE TABLE recipeServing ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, recipeId TEXT NOT NULL, name TEXT NOT NULL, amountOfBaseUnit REAL, servingLabel TEXT, servingOption TEXT, servingQuantity REAL, isLiquid INTEGER, note TEXT, productId TEXT, producer TEXT );

CREATE TABLE recipeTag( recipeId TEXT NOT NULL REFERENCES recipe, tag TEXT NOT NULL, PRIMARY KEY (recipeId, tag) );

CREATE TABLE recipeTag( recipeId TEXT NOT NULL, tag TEXT NOT NULL );

CREATE TABLE seenStory( storyId TEXT PRIMARY KEY NOT NULL );

CREATE TABLE storyProgress ( storyId TEXT PRIMARY KEY NOT NULL, lastSeenPage INTEGER NOT NULL );

CREATE TABLE userProperties ( id INTEGER PRIMARY KEY, gender INTEGER NOT NULL, token TEXT NOT NULL, CHECK(id=1) );

```

## 2. Модули ИИ-трекинга в YAZIO (`aifoodtracking`, `aivoicemultitracking`, `aiinsightsdaily`)

- `yazio/aifoodtracking/api/nutrimind/data/NutriMindExperiment`
- `yazio/aifoodtracking/api/snapit/camera/permission/CameraPermissionStatus`
- `yazio/aifoodtracking/presenter/components/AiRefineSearchAction`
- `yazio/aifoodtracking/presenter/components/AiSwitchTrackingMethodAction`
- `yazio/aifoodtracking/presenter/snapit/camera/navigation/AiSnapItCameraNavigator`
- `yazio/aifoodtracking/presenter/snapit/camera/ui/AiSnapItCameraAction`
- `yazio/aifoodtracking/presenter/snapit/images/AiFoodTrackingLimitHitImage`
- `yazio/aifoodtracking/presenter/snapit/images/AiFoodTrackingSnapItImage`
- `yazio/aifoodtracking/presenter/snapit/result/AiSnapItResultAction`
- `yazio/aifoodtracking/presenter/snapit/result/navigation/AiSnapItResultNavigator`
- `yazio/aifoodtracking/presenter/snapit/tutorial/ui/AiSnapItTutorialImage`
- `yazio/aiinsightsdaily/api/entity/AiInsightsDailyTipsType`
- `yazio/aiinsightsdaily/api/tracking/DiaryInsightsCardStatusTrackingEvent`
- `yazio/aiinsightsdaily/api/unlock/UnlockProgressDay`
- `yazio/aiinsightsdaily/presenter/AiInsightsDailyAction`
- `yazio/aiinsightsdaily/presenter/AiInsightsDailyNavigator`
- `yazio/aiinsightsdaily/presenter/diary/DiaryAiInsightsDailyCardNavigator`
- `yazio/aitextvoicefoodtracking/presenter/input/AiTextVoiceFoodTrackingInputAction`
- `yazio/aitextvoicefoodtracking/presenter/input/AiTextVoiceFoodTrackingInputNavigator`
- `yazio/aitextvoicefoodtracking/presenter/input/a`
- `yazio/aitextvoicefoodtracking/presenter/input/b`
- `yazio/aitextvoicefoodtracking/presenter/input/c`
- `yazio/aitextvoicefoodtracking/presenter/result/AiTextVoiceFoodTrackingResultAction`
- `yazio/aitextvoicefoodtracking/presenter/result/AiTextVoiceFoodTrackingResultNavigator`
- `yazio/aitextvoicefoodtracking/ui/input/components/MicrophoneButtonState`
- `yazio/aivoicemultitracking/implementation/network/DistanceUnitDto`
- `yazio/aivoicemultitracking/presenter/input/AiVoiceMultiTrackingInputAction`
- `yazio/aivoicemultitracking/presenter/input/AiVoiceMultiTrackingInputState`
- `yazio/aivoicemultitracking/presenter/input/navigation/AiVoiceMultiTrackingInputNavigator`
- `yazio/aivoicemultitracking/presenter/input/viewstate/AiVoiceMultiTrackingErrorIllustration`
- `yazio/aivoicemultitracking/presenter/input/viewstate/AiVoiceMultiTrackingInputViewState`
- `yazio/aivoicemultitracking/presenter/input/viewstate/AiVoiceMultiTrackingRecordButtonIcon`
- `yazio/aivoicemultitracking/presenter/result/AiVoiceMultiTrackingResultAction`
- `yazio/aivoicemultitracking/presenter/result/navigation/AiVoiceMultiTrackingResultNavigator`
- `yazio/aivoicemultitracking/presenter/result/viewstate/AiVoiceMultiTrackingIcon`
- `yazio/aivoicemultitracking/ui/input/components/PhaseKind`
- `yazio/aivoicemultitracking/ui/input/components/a`
- `yazio/aivoicemultitracking/ui/input/components/b`
- `yazio/featureflags/aiinsightsdaily/AiInsightsDailyVariant`

## 3. Модули расчёта целей, калорий и выходного буфера (`goals`, `energy`, `nutrients`)

- `yazio/common/configurableflow/onboarding/funnel/personalPlan/PlanGoalDate`
- `yazio/fasting/api/template/domain/FastingGoal`
- `yazio/fasting/api/template/dto/FastingGoalDTO`
- `yazio/goal/api/CalorieGoalColor`
- `yazio/goal/api/CalorieGoalOverrideMode`
- `yazio/legacy/features/recipes/ui/detail/databinding/RecipeDetailNutrientsBinding`
- `yazio/legacy/features/settings/databinding/SettingsGoalsBinding`
- `yazio/legacy/features/settings/databinding/SettingsGoalsEnergyBinding`
- `yazio/legacy/features/settings/databinding/SettingsGoalsEnergyDistributionBinding`
- `yazio/legacy/features/settings/databinding/SettingsGoalsInfoCardBinding`
- `yazio/legacy/features/settings/databinding/SettingsGoalsNutritionsBinding`
- `yazio/nutrient/api/Nutrient`
- `yazio/nutrient/api/content/NutrientCategory`
- `yazio/nutrient/api/content/NutrientVisibility`
- `yazio/nutrient/api/content/NutrientWeightUnit`
- `yazio/nutrient_summary/NutrientSummaryView`
- `yazio/product/api/rating/ProductRatingNutrient`
- `yazio/recipe/api/model/RecipeEnergyFilter`
- `yazio/settings/goals/GoalSettingType`
- `yazio/settings/goals/GoalSettingsController`
- `yazio/settings/goals/energy/EnergySettingType`
- `yazio/settings/goals/energy/EnergySettingsController`
- `yazio/settings/goals/energy/WeekendCaloriesOption`
- `yazio/settings/goals/energy/distribution/EnergyDistributionController`
- `yazio/settings/goals/nutrition/NutritionGoalsController`
- `yazio/settings/goals/nutrition/NutritionGoalsViewEffect`
- `yazio/settings/presenter/WeekendCaloriesOption`
- `yazio/settings/presenter/caloriedistribution/a`
- `yazio/settings/presenter/caloriedistribution/b`
- `yazio/settings/presenter/caloriedistribution/c`
- `yazio/settings/presenter/caloriedistribution/d`
- `yazio/settings/presenter/caloriedistribution/e`
- `yazio/settings/presenter/caloriegoal/a`
- `yazio/settings/presenter/caloriegoal/b`
- `yazio/settings/presenter/caloriegoal/c`
- `yazio/settings/presenter/caloriegoal/d`
- `yazio/settings/presenter/caloriegoal/e`
- `yazio/settings/presenter/nutrient/a`
- `yazio/settings/presenter/nutrient/b`
- `yazio/settings/presenter/nutrient/c`
- `yazio/settings/presenter/nutrient/d`
- `yazio/units/api/BaseNutrient`
- `yazio/units/api/Energy`
- `yazio/units/api/EnergyDistributionPlan`
- `yazio/units/api/EnergyUnit`
- `yazio/units/api/dto/EnergyUnitDTO`
- `yazio/user/api/OverallGoal`
- `yazio/user/api/dto/OverallGoalDTO`
- `yazio/weightprogresscalculator/api/GoalImpact`
- `yazio/weightprogresscalculator/api/GoalImpactColor`
- `yazio/weightprogresscalculator/api/WeightGoalDirection`

## 4. Модули монетизации, подписок и пейволлов (`paywall`, `subscription`, `payment`)

- `yazio/common/configurableflow/common/subscriptionExplanation/components/SubscriptionJourneyItemIconType`
- `yazio/featureflag/api/model/ShopRewardAdPlacement`
- `yazio/featureflags/aftermealtracking/ProBenefitsAnimationRebrandVariant`
- `yazio/featureflags/monetization/SubscriptionSettingsRebrandVariant`
- `yazio/featureflags/shop/DebugShopItemExpiredVariant`
- `yazio/legacy/features/settings/databinding/SettingsSubscriptionsBinding`
- `yazio/legacy/features/settings/databinding/SettingsSubscriptionsCancelRowBinding`
- `yazio/legacy/features/settings/databinding/SettingsSubscriptionsGatewayBinding`
- `yazio/payment/api/playpayment/model/BillingResponse`
- `yazio/payment/api/playpayment/model/ProductType`
- `yazio/payment/api/playpayment/model/SkuWithType`
- `yazio/payment/api/purchase/PurchaseDelegate`
- `yazio/payment/api/purchase/PurchaseErrorType`
- `yazio/payment/api/purchase/PurchaseTrackEvent`
- `yazio/payment/api/purchase/PurchaseType`
- `yazio/payment/api/purchase/RenewalPurchaseDelegate`
- `yazio/payment/api/purchase/funnel/PaywallFunnelSource`
- `yazio/payment/api/sku/PurchaseKey`
- `yazio/payment/api/subscription/StorePremiumStatus`
- `yazio/payment/api/subscription/SubscriptionPeriod`
- `yazio/payment/api/success/PurchaseSuccessListener`
- `yazio/payment/implementation/playpayment/ConnectionState`
- `yazio/payment/implementation/playpayment/a`
- `yazio/payment/implementation/playpayment/b`
- `yazio/payment/implementation/playpayment/c`
- `yazio/payment/implementation/purchase/PurchaseRequestDTO`
- `yazio/paywall/api/diaryoffer/DiaryOfferPaywallType`
- `yazio/paywall/api/diaryoffer/DiaryOfferPurchaseDelegate`
- `yazio/paywall/presenter/diaryoffer/DiaryOfferNavigator`
- `yazio/paywall/presenter/diaryoffer/activeuser/DiaryOfferPaywallAction`
- `yazio/paywall/presenter/diaryoffer/activeuser/DiaryOfferPaywallImage`
- `yazio/paywall/presenter/diaryoffer/activeuser/DiaryOfferPaywallNavigator`
- `yazio/paywall/presenter/diaryoffer/activeuser/DiaryOfferPaywallVariant`
- `yazio/paywall/presenter/diaryoffer/finishedflow/FlowDiaryOfferPaywallAction`
- `yazio/paywall/presenter/diaryoffer/finishedflow/FlowDiaryOfferPaywallNavigator`
- `yazio/paywall/presenter/winback/WinBackNavigator`
- `yazio/paywall/ui/cards/yettie/YettiePurchaseCardStyle`
- `yazio/paywall/ui/offer/card/items/StrikethroughPriceLabelMode`
- `yazio/paywall/ui/offer/content/YettiePriceCardStyle`
- `yazio/settings/account/subscription/subscriptionsettings/SubscriptionAction`
- `yazio/settings/account/subscription/subscriptionsettings/SubscriptionSettingsController`
- `yazio/settings/account/subscription/subscriptionsettings/SubscriptionState`
- `yazio/settings/account/subscription/subscriptionsettings/a`
- `yazio/settings/account/subscription/subscriptionsettings/b`
- `yazio/shop/implementation/network/dto/CurrencyTypeDto`
- `yazio/shop/presenter/collectmore/CollectMoreAction`
- `yazio/shop/presenter/collectmore/CollectMoreNavigator`
- `yazio/shop/presenter/currencyearned/CurrencyEarnedAction`
- `yazio/shop/presenter/currencyearned/CurrencyEarnedNavigator`
- `yazio/shop/presenter/expired/ShopItemExpiredAction`
- `yazio/shop/presenter/navigation/ShopItemExpiredNavigator`
- `yazio/shop/presenter/overview/ShopAction`
- `yazio/shop/presenter/overview/navigation/ShopOverviewNavigator`
- `yazio/shop/presenter/purchase/confirmation/PurchaseConfirmationAction`
- `yazio/shop/presenter/purchase/confirmation/navigation/PurchaseConfirmationNavigator`
- `yazio/shop/presenter/purchase/full/PurchaseFullAction`
- `yazio/shop/presenter/purchase/full/PurchaseFullNavigator`
- `yazio/shop/presenter/purchase/successful/PurchaseSuccessfulAction`
- `yazio/shop/presenter/purchase/successful/PurchaseSuccessfulNavigator`
- `yazio/subscription/api/SubscriptionGateway`
- `yazio/subscription/api/SubscriptionStatus`
- `yazio/subscription/presenter/SubscriptionNavigator`
- `yazio/subscription/presenter/SubscriptionSettingsAction`
- `yazio/subscription/presenter/subscriptionbenefit/SubscriptionBenefitEvent`
- `yazio/subscription/presenter/subscriptionbenefit/SubscriptionBenefitNavigator`
- `yazio/user/api/account/PaymentProvider`

## 5. Модули интервального голодания (`fasting`)

- `yazio/diary/presentation/fasting/DiaryFastingCardAction`
- `yazio/diary/presentation/fasting/DiaryFastingCardImage`
- `yazio/diary/presentation/fasting/DiaryFastingCardNavigator`
- `yazio/diary/presentation/summary/viewstate/DiaryDaySummaryFastingStyle`
- `yazio/diary/summary/overview/BaselineDiaryDaySummaryFastingStyle`
- `yazio/fasting/api/model/FastingTrackerCard`
- `yazio/fasting/api/template/FastingType`
- `yazio/fasting/api/template/domain/FastingDifficulty`
- `yazio/fasting/api/template/domain/FastingFlexibility`
- `yazio/fasting/api/template/domain/FastingGoal`
- `yazio/fasting/api/template/domain/FastingTemplateIcon`
- `yazio/fasting/api/template/dto/FastingDifficultyDTO`
- `yazio/fasting/api/template/dto/FastingFlexibilityDTO`
- `yazio/fasting/api/template/dto/FastingGoalDTO`
- `yazio/fasting/api/template/dto/FastingTemplateIconDTO`
- `yazio/fasting/api/template/dto/FastingTypeDTO`
- `yazio/fasting/presenter/FastingStageState`
- `yazio/fasting/presenter/FastingStageType`
- `yazio/fasting/presenter/chart/segment/FastingChartSegmentStyle`
- `yazio/fasting/presenter/counter/FastingCounterDirection`
- `yazio/fasting/presenter/history/FastingHistoryType`
- `yazio/fasting/presenter/history/statistics/FastingStatisticType`
- `yazio/fasting/presenter/notification/FastingStageNotificationType`
- `yazio/fasting/presenter/patch/FastingPatchDirection`
- `yazio/fasting/presenter/picker/FastingPickerAction`
- `yazio/fasting/ui/chart/FastingChartView`
- `yazio/fasting/ui/chart/bar/FastingBarStyle`
- `yazio/fasting/ui/chart/bar/FastingBarView`
- `yazio/fasting/ui/chart/history/FastingHistoryChartViewType`
- `yazio/fasting/ui/chart/history/tooltip/FastingHistoryTooltipItemView`
- `yazio/fasting/ui/chart/history/tooltip/FastingHistoryTooltipView`
- `yazio/fasting/ui/chart/history/tooltip/FastingTooltipClickEvent`
- `yazio/fasting/ui/chart/history/tooltip/TooltipIndicatorPosition`
- `yazio/fasting/ui/chart/legend/FastingChartLegend`
- `yazio/fasting/ui/chart/legend/FastingChartLegendStyle`
- `yazio/fasting/ui/chart/legend/item/FastingChartLegendItem`
- `yazio/fasting/ui/chart/separator/FastingChartSeparator`
- `yazio/fasting/ui/common/FastingPlanStyle`
- `yazio/fasting/ui/common/FastingTrackerTimeView`
- `yazio/fasting/ui/common/FastingTrackerTimeViewStyle`
- `yazio/fasting/ui/detail/FastingViewEffect`
- `yazio/fasting/ui/detail/items/headline/FastingDetailHeadline`
- `yazio/fasting/ui/history/FastingHistoryController`
- `yazio/fasting/ui/history/items/header/FastingHistoryHeaderType`
- `yazio/fasting/ui/overview/FastingOverviewController`
- `yazio/fasting/ui/overview/items/FastingItemsOrder`
- `yazio/fasting/ui/overview/items/FastingSection`
- `yazio/fasting/ui/overview/items/header/FastingOverviewHeaderActionType`
- `yazio/fasting/ui/overview/items/header/FastingOverviewHeaderType`
- `yazio/fasting/ui/overview/plans/FastingPlansOverviewController`
- `yazio/fasting/ui/quiz/pages/notrecommended/FastingNotRecommendedController`
- `yazio/fasting/ui/quiz/pages/question/QuizFollowUpController`
- `yazio/fasting/ui/quiz/pages/recommended/FastingRecommendedController`
- `yazio/fasting/ui/quiz/pages/recommended/a`
- `yazio/fasting/ui/quiz/pages/recommended/b`
- `yazio/fasting/ui/tracker/items/tracker/FastingTrackerCircleStyle`
- `yazio/fasting/ui/tracker/items/tracker/FastingTrackerPatchView`
- `yazio/fasting/ui/tracker/items/tracker/indicator/FastingTrackerActivePage`
- `yazio/fasting/ui/tracker/items/tracker/indicator/FastingTrackerIndicator`
- `yazio/fasting/ui/tracker/progress/FastingTrackerProgressRing`
- `yazio/fasting/ui/tracker/progress/FastingTrackerProgressView`
- `yazio/fasting/ui/tracker/share/FastingTrackerShareType`
- `yazio/fasting/ui/tracker/stages/FastingTrackerStagesView`
- `yazio/legacy/features/fasting/ui/detail/databinding/FastingBinding`
- `yazio/legacy/features/fasting/ui/detail/databinding/FastingCancelBinding`
- `yazio/legacy/features/fasting/ui/detail/databinding/FastingDetailHeadlineBinding`
- `yazio/legacy/features/fasting/ui/detail/databinding/FastingPickerBinding`
- `yazio/legacy/features/fasting/ui/detail/databinding/FastingTeaserBinding`
- `yazio/legacy/features/fasting/ui/detail/databinding/FastingTimesBinding`
- `yazio/legacy/features/fasting/ui/detail/databinding/FastingTimesPresetRowBinding`
- `yazio/legacy/features/fasting/ui/detail/databinding/FastingTipBinding`
- `yazio/legacy/features/fasting/ui/history/databinding/FastingHistoryBinding`
- `yazio/legacy/features/fasting/ui/history/databinding/FastingHistoryChartBinding`
- `yazio/legacy/features/fasting/ui/history/databinding/FastingHistoryChartItemBinding`
- `yazio/legacy/features/fasting/ui/history/databinding/FastingHistoryHeaderBinding`
- `yazio/legacy/features/fasting/ui/history/databinding/FastingHistoryMostUsedTrackerBinding`
- `yazio/legacy/features/fasting/ui/history/databinding/FastingHistoryMostUsedTrackerItemBinding`
- `yazio/legacy/features/fasting/ui/history/databinding/FastingHistoryStatisticItemBinding`
- `yazio/legacy/features/fasting/ui/overview/databinding/FastingOverviewBinding`
- `yazio/legacy/features/fasting/ui/overview/databinding/FastingOverviewHeaderBinding`
- `yazio/legacy/features/fasting/ui/overview/databinding/FastingOverviewPlansBinding`
- `yazio/legacy/features/fasting/ui/overview/databinding/FastingOverviewPlansItemBinding`
- `yazio/legacy/features/fasting/ui/overview/databinding/FastingOverviewQuizBinding`
- `yazio/legacy/features/fasting/ui/overview/databinding/FastingOverviewQuoteBinding`
- `yazio/legacy/features/fasting/ui/overview/databinding/FastingTrackerOverviewBinding`
- `yazio/legacy/features/fasting/ui/quiz/databinding/FastingQuizPageFollowUpQuestionBinding`
- `yazio/legacy/features/fasting/ui/quiz/databinding/FastingQuizPageNotRecommendedBinding`
- `yazio/legacy/features/fasting/ui/quiz/databinding/FastingQuizPageQuestionBinding`
- `yazio/legacy/features/fasting/ui/quiz/databinding/FastingQuizPageRecommendedBinding`
- `yazio/legacy/features/fasting/ui/quiz/databinding/FastingQuizPageRecommendedItemHeaderBinding`
- `yazio/legacy/features/fasting/ui/quiz/databinding/FastingQuizQuestionItemBinding`
- `yazio/legacy/features/fasting/ui/quiz/databinding/FastingQuizRootBinding`
- `yazio/legacy/features/fasting/ui/tracker/databinding/FastingTrackerActiveBinding`
- `yazio/legacy/features/fasting/ui/tracker/databinding/FastingTrackerActiveChartBinding`
- `yazio/legacy/features/fasting/ui/tracker/databinding/FastingTrackerActiveCounterBinding`
- `yazio/legacy/features/fasting/ui/tracker/databinding/FastingTrackerActiveHistoryBinding`
- `yazio/legacy/features/fasting/ui/tracker/databinding/FastingTrackerActiveStagesBinding`
- `yazio/notifications/api/model/FastingNotificationCard`

## 6. Пошаговая расшифровка реальных экранов из снятых XML-дампов

### Экран `01_onboarding_goal.xml`
- **Тексты на экране:** What’s your main goal? | Lose weight | Eat healthier without losing weight | Gain weight | Build muscle | Something else | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `01_onboarding_resumed.xml`
- **Тексты на экране:** What’s your main goal? | Lose weight | Eat healthier without losing weight | Gain weight | Build muscle | Something else | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `02_onboarding_step.xml`
- **Тексты на экране:** Allow Yazio to send you notifications? | Allow | Don’t allow
- **UI IDs:** `content`, `grant_singleton`, `grant_dialog`, `content_container`, `permission_icon`, `permission_message`, `permission_allow_button`, `permission_deny_button`

### Экран `02_permission_notifications.xml`
- **Тексты на экране:** Allow Yazio to send you notifications? | Allow | Don’t allow
- **UI IDs:** `content`, `grant_singleton`, `grant_dialog`, `content_container`, `permission_icon`, `permission_message`, `permission_allow_button`, `permission_deny_button`

### Экран `03_attribution.xml`
- **Тексты на экране:** How did you hear about Yazio? | Instagram | Facebook | TikTok | YouTube | Friends and family | Creator or influencer | AI Chat (e.g. ChatGPT) | Coupon website | Search engine (e.g., Google) | Google Play | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `03_onboarding_question.xml`
- **Тексты на экране:** How did you hear about Yazio? | Instagram | Facebook | TikTok | YouTube | Friends and family | Creator or influencer | AI Chat (e.g. ChatGPT) | Coupon website | Search engine (e.g., Google) | Google Play | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `04_onboarding_gender.xml`
- **Тексты на экране:** What's your sex? | Since the formula for an accurate calorie calculation differs based on sex, we need this information to calculate your daily calorie goal. | Female | Male | Which sex should I select? | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.text.binary_subtitle`, `onboarding.button.onboarding_binary_select_option_0`, `onboarding.button.onboarding_binary_select_option_1`

### Экран `05_onboarding_birthdate.xml`
- **Тексты на экране:** Pick the name that suits you best | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.ask_username`, `onboarding.text_field.weight_text_field`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `06_onboarding_birthdate.xml`
- **Тексты на экране:** Why do you want to lose weight? | To feel more confident | To improve my overall health | To increase my fitness level | To prepare for a special event | Something else | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `07_onboarding_step.xml`
- **Тексты на экране:** Is there anything else you want to achieve? | Improve my relationship with food | Learn how to cook healthily | Strengthen my immune system | Sleep better and have more energy | Feel comfortable in my own skin | None of the above | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `08_onboarding_step.xml`
- **Тексты на экране:** I’ll use Yazio to... | track my progress daily so I can follow through on my goals. | Tap and hold the icon to commit | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `shared_element.button.back`

### Экран `09_onboarding_committed.xml`
- **Тексты на экране:** What experience do you have with weight loss? | I've lost weight before and want to lose more. | I've tried to lose weight before but was unsuccessful. | I've lost weight before but gained it back. | I'm on weight loss medication to support my journey (Wegovy®, Zepbound®, etc.). | I've never tried to lose weight before. | Continue | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `09_onboarding_step.xml`
- **Тексты на экране:** I’ll use Yazio to... | track my progress daily so I can follow through on my goals. | Tap and hold the icon to commit | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `shared_element.button.back`

### Экран `10_onboarding_step.xml`
- **Тексты на экране:** Restrictive dieting can cause a yo-yo effect. | According to a study from Columbia University, those with a history of yo-yo dieting had increased cardiovascular risks compared to those who maintained a consistent weight. | The Asian Association for the Study of Diabetes states that frequent, significant weight changes can increase the risk of diabetes and contribute to increased belly fat. | Continue | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.affirmation_why_other_diets_fail_title`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `11_onboarding_step.xml`
- **Тексты на экране:** Restrictive dieting can cause a yo-yo effect. | According to a study from Columbia University, those with a history of yo-yo dieting had increased cardiovascular risks compared to those who maintained a consistent weight. | The Asian Association for the Study of Diabetes states that frequent, significant weight changes can increase the risk of diabetes and contribute to increased belly fat. | Continue | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.affirmation_why_other_diets_fail_title`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `11_sustainable_weight_loss.xml`
- **Тексты на экране:** Say hello to simple, sustainable weight loss! | With Yazio, you can eat what you want. No more giving up foods or following complex "rules." | We help you achieve sustainable weight loss in a way that suits your lifestyle. | Continue | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.affirmation_why_other_diets_fail_title`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `12_onboarding_question.xml`
- **Тексты на экране:** What challenges did you face? | Resisting cravings | Staying motivated | Reducing portion sizes | Knowing what to eat | Being too busy | Something else | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `12_onboarding_step.xml`
- **Тексты на экране:** Restrictive dieting can cause a yo-yo effect. | According to a study from Columbia University, those with a history of yo-yo dieting had increased cardiovascular risks compared to those who maintained a consistent weight. | The Asian Association for the Study of Diabetes states that frequent, significant weight changes can increase the risk of diabetes and contribute to increased belly fat. | Continue | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.affirmation_why_other_diets_fail_title`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `13_onboarding_step.xml`
- **Тексты на экране:** We’ll help you through it. | Losing weight can be challenging, but you're not alone. We'll be with you every step of the way, giving you everything you need to achieve your goals. | Let's Go | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.affirmation_title`, `onboarding.text.affirmation_subtitle`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `14_impact_on_weight.xml`
- **Тексты на экране:** What’s had the biggest impact on your weight? | Injury or health issue | Work or lifestyle changes | Age-related changes | Stress or mental health | Medication | Something else | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `14_onboarding_step.xml`
- **Тексты на экране:** We’ll help you through it. | Losing weight can be challenging, but you're not alone. We'll be with you every step of the way, giving you everything you need to achieve your goals. | Let's Go | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.affirmation_title`, `onboarding.text.affirmation_subtitle`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `15_after_impact.xml`
- **Тексты на экране:** Think back to your last weight-loss journey. Has anything changed since then? | Yes | No | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_binary_select_option_0`, `onboarding.button.onboarding_binary_select_option_1`, `shared_element.button.back`

### Экран `16_after_changed.xml`
- **Тексты на экране:** Think about someone you know who has achieved their goal. What was the key to success? | Intrinsic willpower | Structure and planning | Healthy habits | Good support system | I don’t know | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `16_key_to_success.xml`
- **Тексты на экране:** Think about someone you know who has achieved their goal. What was the key to success? | Intrinsic willpower | Structure and planning | Healthy habits | Good support system | I don’t know | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `17_screen.xml`
- **Тексты на экране:** You can do it, too! | There are several factors that play a role in success. While willpower and mental strength can be important, a bulletproof plan and reliable support system are absolutely essential. That's exactly what you have Yazio for now. | I Can't Wait | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.affirmation_title`, `onboarding.text.affirmation_subtitle`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `18_screen.xml`
- **Тексты на экране:** Have you ever tracked calories before? | Yes | No | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_binary_select_option_0`, `onboarding.button.onboarding_binary_select_option_1`, `shared_element.button.back`

### Экран `19_after_tracked_before.xml`
- **Тексты на экране:** See what gives your progress a boost | Great—you’re already building habits that support your goals! We’ll help you spot what’s working so you can focus on choices that move you forward. | Got It | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.affirmation_title`, `onboarding.text.affirmation_subtitle`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `19_screen.xml`
- **Тексты на экране:** Have you ever tracked calories before? | Yes | No | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_binary_select_option_0`, `onboarding.button.onboarding_binary_select_option_1`, `shared_element.button.back`

### Экран `20_boost_next.xml`
- **Тексты на экране:** How did you count calories in the past? | Using an app | Using a website | Using pen and paper | Using a spreadsheet | Using a calculator | Using mental math | Other | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `21_past_app_next.xml`
- **Тексты на экране:** Which app did you use? | Yazio | MyFitnessPal | Lifesum | LoseIt! | WW (Weight Watchers) | Noom | FatSecret | Other | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `22_competitor_why_stopped.xml`
- **Тексты на экране:** Not bad, but with Yazio, you’ve definitely made the best choice. You can ... | Track foods in seconds thanks to intuitive handling. | Customize the app to best fit your particular needs. | Count on one-of-a-kind customer care along the way. | Stay motivated and share experiences with our community. | Count Me In | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.affirmation_title`, `onboarding.card.affirmation_benefits_of_pro`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `23_after_benefits.xml`
- **Тексты на экране:** Track smarter with AI | Smart food tracking is here. Snap a photo and get instant nutrition info with AI—no manual entry needed. | Continue | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.page.ai_intro`, `onboarding.image.ai_intro_image`, `onboarding.text.ai_intro_title`, `onboarding.text.ai_intro_subtitle`

### Экран `24_screen.xml`
- **Тексты на экране:** Last time you counted calories, did you find it difficult to stick to your daily calorie goal? | Yes | No | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_binary_select_option_0`, `onboarding.button.onboarding_binary_select_option_1`, `shared_element.button.back`

### Экран `25_screen.xml`
- **Тексты на экране:** That's a thing of the past! | No more going to bed hungry or giving up your favorite foods. With our huge recipe database, easy-to-use features and helpful nutrition tips, sticking to your calorie goal will be fun and easy. | Sounds Amazing | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.affirmation_title`, `onboarding.text.affirmation_subtitle`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `26_screen.xml`
- **Тексты на экране:** Have you ever tried intermittent fasting? | Yes, I liked it. | Yes, but it wasn’t for me. | No, but I’d like to try it. | No, I’m not interested. | What’s intermittent fasting? | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `27_screen.xml`
- **Тексты на экране:** Say hello to the ultimate dream team. | Calorie counting and intermittent fasting work very well together. With Yazio, you’ll have customizable fasting trackers and a comprehensive calorie counter bundled into one. Creating healthy, sustainable habits has never been easier. | Love It | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.affirmation_title`, `onboarding.text.affirmation_subtitle`, `shared_element.button.next_button`, `shared_element.button.back`

### Экран `28_screen.xml`
- **Тексты на экране:** How do you plan to stay on track? | I’m going to log all my meals before I eat. | I’m going to get an accountability partner. | I’m going to meal prep and use recipes to plan ahead. | I’m going to see how long my tracking streak can get. | I'm going to pay attention to my calorie intake. | I’m not sure yet. | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `29_screen.xml`
- **Тексты на экране:** How do you feel about starting your journey? | Motivated | Confident | Nervous | Frustrated | Unmotivated | I’m not sure | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `current.xml`
- **Тексты на экране:** Have you ever tracked calories before? | Yes | No | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_binary_select_option_0`, `onboarding.button.onboarding_binary_select_option_1`, `shared_element.button.back`

### Экран `current_state.xml`
- **Тексты на экране:** What’s had the biggest impact on your weight? | Injury or health issue | Work or lifestyle changes | Age-related changes | Stress or mental health | Medication | Something else | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `fatsecret_check.xml`
- **Тексты на экране:** Close sheet | Calorie Counter by fatsecret | fatsecret | In-app purchases | Average rating 4.7 stars in 536 thousand reviews | Content rating Rated for 3+ | 54 MB | Downloaded 50 million plus times | Install | Screenshot 1 of 8 | Screenshot 2 of 8 | Screenshot 3 of 8 | Screenshot 4 of 8 | About this app | Learn more About this app
- **UI IDs:** `0_resource_name_obfuscated`, `content`

### Экран `screen_after_get_started.xml`
- **Тексты на экране:** What’s your main goal? | Lose weight | Eat healthier without losing weight | Gain weight | Build muscle | Something else | Next | Back
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_back_screen.text.welcome_back_text`, `onboarding.text.title`, `onboarding.button.onboarding_flow_select_option_0`, `onboarding.button.onboarding_flow_select_option_1`, `onboarding.button.onboarding_flow_select_option_2`

### Экран `test_start.xml`
- **Тексты на экране:** 100 million | happy users | 20 million | foods for calorie tracking | Let’s make every day count! | Get Started | I already have an account
- **UI IDs:** `action_bar_root`, `content`, `coordinator`, `compose`, `mainControllerContainer`, `welcome_screen`, `welcome_screen.text.welcome_text`, `welcome_screen.button.get_started_button`, `welcome_screen.button.already_have_account_button`, `welcome_screen.button.yazio_logo`

