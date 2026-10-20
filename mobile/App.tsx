import React, { useState } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  TextInput,
  StyleSheet,
  Modal,
  Alert,
} from 'react-native';

/**
 * YAZIO-Next Mobile Application (React Native / Expo).
 * Implements all 5 core sections documented in docs/YAZIO_INTERNAL_SCREENS_MAP.md:
 * 1. Diary (Screens 40-42) - Calorie ring 1,838 Cal, macros, 4 meals, water glasses, fasting/weight widgets
 * 2. Add Food (Screens 50-53) - Search, grams picker, barcode scanner, 3 free AI camera scans
 * 3. Fasting (Screens 60-61) - 12:12 Free / 16:8 PRO timer with autophagy/fat-burning phases
 * 4. Recipes (Screens 70-71) - Calorie range filters (100-200, 300-400 Cal) & 1-tap "Add to Diary"
 * 5. Profile & PRO (Screens 31-33, 80-81) - Goals 50% C / 20% P / 30% F, Paywall & 75% Spinning Wheel
 */

interface ConsumedFood {
  id: string;
  name: string;
  meal: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  grams: number;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'diary' | 'add' | 'fasting' | 'recipes' | 'profile'>('diary');

  // Goals (Verified from YAZIO screen 81_nutrient_goals_detail)
  const [dailyCalorieGoal, setDailyCalorieGoal] = useState(1838);
  const macroGoals = { carbs: 224, protein: 90, fat: 59 }; // 50% / 20% / 30%
  const mealTargets = { breakfast: 551, lunch: 735, dinner: 459, snack: 92 }; // 30% / 40% / 25% / 5%

  // Diary State
  const [selectedDayOffset, setSelectedDayOffset] = useState<number>(0); // 0 = Today, 1 = Tomorrow (Free!)
  const [consumedItems, setConsumedItems] = useState<ConsumedFood[]>([
    { id: '1', name: 'Coffee with Milk', meal: 'breakfast', grams: 200, calories: 45, protein: 3.2, carbs: 4.8, fat: 1.5 },
  ]);
  const [waterGlasses, setWaterGlasses] = useState(3); // 3 * 250ml = 750ml

  // Food Search & Picker State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<any | null>(null);
  const [selectedPortionGrams, setSelectedPortionGrams] = useState(150);
  const [targetMeal, setTargetMeal] = useState<'breakfast' | 'lunch' | 'dinner' | 'snack'>('breakfast');

  // Fasting State
  const [fastingActive, setFastingActive] = useState(true);
  const [fastingProtocol, setFastingProtocol] = useState<'12:12' | '16:8'>('12:12');

  // Monetization & Modals State
  const [freeAiScansLeft, setFreeAiScansLeft] = useState(3);
  const [isProUser, setIsProUser] = useState(false);
  const [showPaywall, setShowPaywall] = useState(false);
  const [showSpinWheel, setShowSpinWheel] = useState(false);

  // Computations
  const totalEaten = consumedItems.reduce((acc, item) => acc + item.calories, 0);
  const remainingCalories = Math.max(0, dailyCalorieGoal - totalEaten);
  const totalCarbs = consumedItems.reduce((acc, item) => acc + item.carbs, 0);
  const totalProtein = consumedItems.reduce((acc, item) => acc + item.protein, 0);
  const totalFat = consumedItems.reduce((acc, item) => acc + item.fat, 0);

  // Quick food catalog
  const popularCatalog = [
    { name: 'Banana', calories100g: 89, protein100g: 1.1, carbs100g: 22.8, fat100g: 0.3, portion: 150, portionLabel: 'Whole, regular (150g)' },
    { name: 'Scrambled Eggs (2 eggs)', calories100g: 148, protein100g: 12.6, carbs100g: 1.1, fat100g: 10.0, portion: 100, portionLabel: 'Serving (100g)' },
    { name: 'Milbona Skyr (Lidl)', calories100g: 65, protein100g: 11.0, carbs100g: 4.0, fat100g: 0.2, portion: 200, portionLabel: 'Cup (200g)' },
    { name: 'Oatmeal with Water', calories100g: 68, protein100g: 2.4, carbs100g: 12.0, fat100g: 1.4, portion: 250, portionLabel: 'Bowl (250g)' },
  ];

  const handleAddFoodToDiary = (food: { name: string; calories: number; protein: number; carbs: number; fat: number; grams: number }) => {
    const newItem: ConsumedFood = {
      id: Date.now().toString(),
      name: food.name,
      meal: targetMeal,
      grams: food.grams,
      calories: Math.round(food.calories),
      protein: Math.round(food.protein * 10) / 10,
      carbs: Math.round(food.carbs * 10) / 10,
      fat: Math.round(food.fat * 10) / 10,
    };
    setConsumedItems((prev) => [...prev, newItem]);
    setSelectedProduct(null);
    setActiveTab('diary');
  };

  const handleAiPhotoScan = () => {
    if (freeAiScansLeft > 0 || isProUser) {
      if (!isProUser) setFreeAiScansLeft((prev) => prev - 1);
      // Simulate Gemini 3.5 Flash recognition
      const recognizedDish = {
        name: 'Avocado Toast with Poached Egg',
        grams: 220,
        calories: 385,
        protein: 14.2,
        carbs: 26.5,
        fat: 22.0,
      };
      handleAddFoodToDiary(recognizedDish);
      Alert.alert(
        '📸 Gemini 3.5 Flash Erkennung',
        `Gericht erkannt: ${recognizedDish.name} (${recognizedDish.calories} kcal).\nVerbleibende Gratis-Scans: ${isProUser ? 'Unbegrenzt (PRO)' : freeAiScansLeft - 1}`
      );
    } else {
      setShowPaywall(true);
    }
  };

  // -------------------------------------------------------------------------
  // RENDER: DIARY TAB (Screens 40-42)
  // -------------------------------------------------------------------------
  const renderDiaryTab = () => (
    <ScrollView contentContainerStyle={styles.scroll}>
      {/* Date Switcher with Tomorrow support (Pain-point solved!) */}
      <View style={styles.dateRow}>
        <TouchableOpacity
          style={[styles.dateChip, selectedDayOffset === 0 && styles.activeDateChip]}
          onPress={() => setSelectedDayOffset(0)}
        >
          <Text style={[styles.dateChipText, selectedDayOffset === 0 && styles.activeDateChipText]}>
            Heute • Mo, 19. Okt
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.dateChip, selectedDayOffset === 1 && styles.activeDateChip]}
          onPress={() => setSelectedDayOffset(1)}
        >
          <Text style={[styles.dateChipText, selectedDayOffset === 1 && styles.activeDateChipText]}>
            Morgen • Di, 20. Okt 🔓 (Gratis)
          </Text>
        </TouchableOpacity>
      </View>

      {/* Top Calorie Ring & Macros Summary (Screen 40) */}
      <View style={styles.card}>
        <View style={styles.cardHeaderRow}>
          <Text style={styles.cardTitle}>Tagesbilanz</Text>
          <View style={styles.badgeRow}>
            <Text style={styles.badgeText}>💎 12</Text>
            <Text style={styles.badgeText}>🔥 1 Tag Streak</Text>
          </View>
        </View>

        <View style={styles.ringContainer}>
          <View style={styles.calorieCircle}>
            <Text style={styles.calorieBigText}>{remainingCalories}</Text>
            <Text style={styles.calorieSubText}>kcal übrig</Text>
          </View>
          <View style={styles.summaryStats}>
            <Text style={styles.statLine}>Gegessen: <Text style={styles.bold}>{totalEaten}</Text> / {dailyCalorieGoal} kcal</Text>
            <Text style={styles.statLine}>Verbrannt: <Text style={styles.bold}>0</Text> kcal</Text>
            <View style={styles.divider} />
            <Text style={styles.macroMini}>Kohlenhydrate: {Math.round(totalCarbs)} / {macroGoals.carbs} g (50%)</Text>
            <Text style={styles.macroMini}>Eiweiß: {Math.round(totalProtein)} / {macroGoals.protein} g (20%)</Text>
            <Text style={styles.macroMini}>Fett: {Math.round(totalFat)} / {macroGoals.fat} g (30%)</Text>
          </View>
        </View>

        {/* PRO Discount Banner (Spin-the-Wheel trigger) */}
        {!isProUser && (
          <TouchableOpacity style={styles.promoBanner} onPress={() => setShowSpinWheel(true)}>
            <Text style={styles.promoBannerText}>🎡 75% RABATT Glücksrad drehen (Nur noch 2 Std.)</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* 4 Meal Sections (Screen 41: 30% / 40% / 25% / 5%) */}
      {(['breakfast', 'lunch', 'dinner', 'snack'] as const).map((mealKey) => {
        const mealLabels = {
          breakfast: 'Frühstück',
          lunch: 'Mittagessen',
          dinner: 'Abendessen',
          snack: 'Snacks',
        };
        const mealItems = consumedItems.filter((i) => i.meal === mealKey);
        const mealCals = mealItems.reduce((acc, i) => acc + i.calories, 0);

        return (
          <View key={mealKey} style={styles.mealCard}>
            <View style={styles.mealHeader}>
              <View>
                <Text style={styles.mealTitle}>{mealLabels[mealKey]}</Text>
                <Text style={styles.mealTargetText}>
                  {mealCals} / {mealTargets[mealKey]} kcal ({mealKey === 'breakfast' ? '30%' : mealKey === 'lunch' ? '40%' : mealKey === 'dinner' ? '25%' : '5%'})
                </Text>
              </View>
              <TouchableOpacity
                style={styles.addMealBtn}
                onPress={() => {
                  setTargetMeal(mealKey);
                  setActiveTab('add');
                }}
              >
                <Text style={styles.addMealBtnText}>+ Eintragen</Text>
              </TouchableOpacity>
            </View>

            {mealItems.map((item) => (
              <View key={item.id} style={styles.foodRow}>
                <View>
                  <Text style={styles.foodName}>{item.name}</Text>
                  <Text style={styles.foodDetails}>
                    {item.grams}g • P: {item.protein}g | C: {item.carbs}g | F: {item.fat}g
                  </Text>
                </View>
                <Text style={styles.foodCals}>{item.calories} kcal</Text>
              </View>
            ))}
          </View>
        );
      })}

      {/* Water Tracker (Screen 41: 8 Glasses of 250ml) */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Wassertracker ({waterGlasses * 250} / 2000 ml)</Text>
        <Text style={styles.mutedText}>+ Wasser aus Nahrung: 120 ml</Text>
        <View style={styles.glassesRow}>
          {[1, 2, 3, 4, 5, 6, 7, 8].map((g) => (
            <TouchableOpacity
              key={g}
              style={[styles.glassBtn, g <= waterGlasses && styles.glassFilled]}
              onPress={() => setWaterGlasses(g <= waterGlasses ? g - 1 : g)}
            >
              <Text style={styles.glassText}>{g <= waterGlasses ? '💧' : '🥛'}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Fasting & Weight Shortcut (Screen 42) */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Intervallfasten ({fastingProtocol})</Text>
        <Text style={styles.mutedText}>Fastenfenster: 21:00 - 09:00 Uhr (Aktiv)</Text>
        <TouchableOpacity style={styles.secondaryBtn} onPress={() => setActiveTab('fasting')}>
          <Text style={styles.secondaryBtnText}>⏱️ Zum Fasten-Tracker</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );

  // -------------------------------------------------------------------------
  // RENDER: ADD FOOD TAB (Screens 50-53)
  // -------------------------------------------------------------------------
  const renderAddFoodTab = () => (
    <ScrollView contentContainerStyle={styles.scroll}>
      <Text style={styles.screenHeader}>Mahlzeit hinzufügen ({targetMeal})</Text>

      {/* 4 Methods (Screen 50) */}
      <View style={styles.actionMethodsRow}>
        <TouchableOpacity style={[styles.methodCard, styles.aiMethodCard]} onPress={handleAiPhotoScan}>
          <Text style={styles.methodIcon}>📸</Text>
          <Text style={styles.methodTitle}>KI-Foto Scan</Text>
          <Text style={styles.methodSubtitle}>
            {isProUser ? 'PRO Aktiv' : `${freeAiScansLeft} gratis`}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.methodCard}
          onPress={() => {
            Alert.alert('📷 Barcode-Scanner', 'Scanne Barcode: 4008400404127 (Milbona Skyr)');
            const skyr = popularCatalog[2];
            handleAddFoodToDiary({
              name: skyr.name,
              grams: 200,
              calories: skyr.calories100g * 2,
              protein: skyr.protein100g * 2,
              carbs: skyr.carbs100g * 2,
              fat: skyr.fat100g * 2,
            });
          }}
        >
          <Text style={styles.methodIcon}>🔍</Text>
          <Text style={styles.methodTitle}>Barcode</Text>
          <Text style={styles.methodSubtitle}>Gratis (DE & US)</Text>
        </TouchableOpacity>
      </View>

      {/* Search Input */}
      <TextInput
        style={styles.searchInput}
        placeholder="Was hast du gegessen? (z.B. Banane, Haferflocken)"
        placeholderTextColor="#94A3B8"
        value={searchQuery}
        onChangeText={setSearchQuery}
      />

      {/* Product Detail Modal / Picker (Screen 51) */}
      {selectedProduct && (
        <View style={styles.pickerCard}>
          <Text style={styles.pickerTitle}>{selectedProduct.name}</Text>
          <Text style={styles.pickerServingText}>{selectedProduct.portionLabel}</Text>
          <View style={styles.gramInputRow}>
            <Text style={styles.label}>Gramm:</Text>
            <TextInput
              style={styles.gramInput}
              keyboardType="numeric"
              value={selectedPortionGrams.toString()}
              onChangeText={(t) => setSelectedPortionGrams(Number(t) || 100)}
            />
          </View>

          {/* Food Rating Block (YAZIO locks behind PRO, we provide baseline) */}
          <View style={styles.foodRatingBox}>
            <Text style={styles.foodRatingText}>⭐ YAZIO-Next Food Rating: 8.5 / 10 (Ausgewogen)</Text>
          </View>

          <TouchableOpacity
            style={styles.primaryBtn}
            onPress={() => {
              const ratio = selectedPortionGrams / 100.0;
              handleAddFoodToDiary({
                name: selectedProduct.name,
                grams: selectedPortionGrams,
                calories: selectedProduct.calories100g * ratio,
                protein: selectedProduct.protein100g * ratio,
                carbs: selectedProduct.carbs100g * ratio,
                fat: selectedProduct.fat100g * ratio,
              });
            }}
          >
            <Text style={styles.primaryBtnText}>In Tagesplan eintragen</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Frequent Products List (Screen 50) */}
      <Text style={styles.sectionTitle}>Häufige & Beliebte Produkte</Text>
      {popularCatalog.map((prod, idx) => (
        <TouchableOpacity
          key={idx}
          style={styles.catalogItem}
          onPress={() => {
            setSelectedProduct(prod);
            setSelectedPortionGrams(prod.portion);
          }}
        >
          <View>
            <Text style={styles.catalogItemName}>{prod.name}</Text>
            <Text style={styles.catalogItemPortion}>{prod.portionLabel}</Text>
          </View>
          <Text style={styles.catalogItemCals}>
            {Math.round(prod.calories100g * (prod.portion / 100))} kcal
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  // -------------------------------------------------------------------------
  // RENDER: FASTING TAB (Screens 60-61)
  // -------------------------------------------------------------------------
  const renderFastingTab = () => (
    <ScrollView contentContainerStyle={styles.scroll}>
      <Text style={styles.screenHeader}>Intervallfasten</Text>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Protokoll: {fastingProtocol}</Text>
        <Text style={styles.mutedText}>Start: Gestern, 21:00 Uhr • Ende: Heute, 09:00 Uhr</Text>

        <View style={styles.fastingClock}>
          <Text style={styles.fastingBigTime}>10 Std. 45 Min.</Text>
          <Text style={styles.fastingStatusText}>🔥 Fettverbrennung aktiv</Text>
        </View>

        <View style={styles.phasesBox}>
          <Text style={styles.phaseItem}>✓ 4 Std: Blutzuckerspiegel normalisiert</Text>
          <Text style={styles.phaseItem}>✓ 8 Std: Magen & Darm vollständig entlastet</Text>
          <Text style={styles.phaseItemActive}>⚡ 10 Std: Beginn der Fettverbrennung (Jetzt)</Text>
          <Text style={styles.phaseItemLocked}>🔒 16 Std: Zelluläre Autophagie (In PRO freischalten)</Text>
        </View>

        <TouchableOpacity
          style={styles.secondaryBtn}
          onPress={() => setFastingActive(!fastingActive)}
        >
          <Text style={styles.secondaryBtnText}>
            {fastingActive ? 'Fasten beenden' : 'Fasten-Tracker starten'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );

  // -------------------------------------------------------------------------
  // RENDER: RECIPES TAB (Screens 70-71)
  // -------------------------------------------------------------------------
  const renderRecipesTab = () => {
    const recipesList = [
      {
        id: 'rec_1',
        name: 'Blueberry Coconut Shake',
        calories: 358,
        time: '5 Min.',
        difficulty: 'Einfach',
        protein: 24.5,
        carbs: 42.0,
        fat: 8.5,
        tag: '300-400 kcal',
      },
      {
        id: 'rec_2',
        name: 'High Protein Quark Bowl',
        calories: 285,
        time: '3 Min.',
        difficulty: 'Sehr einfach',
        protein: 35.0,
        carbs: 22.0,
        fat: 4.0,
        tag: '200-300 kcal',
      },
    ];

    return (
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.screenHeader}>Gesunde Rezepte</Text>
        <View style={styles.recipeTagsRow}>
          {['Alle', '100-200 kcal', '200-300 kcal', '300-400 kcal', 'High Protein'].map((tag, i) => (
            <View key={i} style={styles.recipeFilterChip}>
              <Text style={styles.recipeFilterText}>{tag}</Text>
            </View>
          ))}
        </View>

        {recipesList.map((rec) => (
          <View key={rec.id} style={styles.recipeCard}>
            <Text style={styles.recipeTitle}>{rec.name}</Text>
            <Text style={styles.recipeDetails}>
              ⏱️ {rec.time} • {rec.difficulty} • {rec.calories} kcal
            </Text>
            <Text style={styles.macroMini}>
              Eiweiß: {rec.protein}g | Carbs: {rec.carbs}g | Fett: {rec.fat}g
            </Text>
            <TouchableOpacity
              style={styles.primaryBtn}
              onPress={() => {
                handleAddFoodToDiary({
                  name: rec.name,
                  grams: 300,
                  calories: rec.calories,
                  protein: rec.protein,
                  carbs: rec.carbs,
                  fat: rec.fat,
                });
                Alert.alert('Rezept hinzugefügt', `${rec.name} wurde in dein Tagebuch übernommen!`);
              }}
            >
              <Text style={styles.primaryBtnText}>+ In Tagesplan übernehmen</Text>
            </TouchableOpacity>
          </View>
        ))}
      </ScrollView>
    );
  };

  // -------------------------------------------------------------------------
  // RENDER: PROFILE & GOALS TAB (Screens 80-81)
  // -------------------------------------------------------------------------
  const renderProfileTab = () => (
    <ScrollView contentContainerStyle={styles.scroll}>
      <Text style={styles.screenHeader}>Mein Profil & Ziele</Text>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Ziel & Makro-Aufteilung</Text>
        <Text style={styles.statLine}>Aktuelles Gewicht: <Text style={styles.bold}>75.0 kg</Text></Text>
        <Text style={styles.statLine}>Zielgewicht: <Text style={styles.bold}>75.0 kg (Gewicht halten)</Text></Text>
        <Text style={styles.statLine}>Tagesziel: <Text style={styles.bold}>{dailyCalorieGoal} kcal</Text></Text>

        <View style={styles.divider} />
        <Text style={styles.bold}>Makronährstoff-Ziele (DGE 4.1 / 4.1 / 9.3 kcal/g):</Text>
        <Text style={styles.macroMini}>• Kohlenhydrate: 224 g (919 kcal) → 50%</Text>
        <Text style={styles.macroMini}>• Eiweiß: 90 g (368 kcal) → 20%</Text>
        <Text style={styles.macroMini}>• Fett: 59 g (551 kcal) → 30%</Text>

        <TouchableOpacity style={styles.proUpgradeBtn} onPress={() => setShowPaywall(true)}>
          <Text style={styles.proUpgradeBtnText}>
            {isProUser ? '✓ YAZIO-Next PRO Aktiv' : '⭐ Auf YAZIO-Next PRO upgraden'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* Dynamic Content View */}
      <View style={styles.content}>
        {activeTab === 'diary' && renderDiaryTab()}
        {activeTab === 'add' && renderAddFoodTab()}
        {activeTab === 'fasting' && renderFastingTab()}
        {activeTab === 'recipes' && renderRecipesTab()}
        {activeTab === 'profile' && renderProfileTab()}
      </View>

      {/* Bottom Navigation Bar (All 5 Tabs) */}
      <View style={styles.bottomNav}>
        {[
          { key: 'diary', label: 'Tagebuch', icon: '📖' },
          { key: 'add', label: '+ Essen', icon: '➕' },
          { key: 'fasting', label: 'Fasten', icon: '⏱️' },
          { key: 'recipes', label: 'Rezepte', icon: '🥗' },
          { key: 'profile', label: 'Profil', icon: '👤' },
        ].map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[styles.navItem, activeTab === tab.key && styles.activeNavItem]}
            onPress={() => setActiveTab(tab.key as any)}
          >
            <Text style={styles.navIcon}>{tab.icon}</Text>
            <Text style={[styles.navLabel, activeTab === tab.key && styles.activeNavLabel]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Paywall Modal (Screen 31) */}
      <Modal visible={showPaywall} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <TouchableOpacity style={styles.closeBtn} onPress={() => setShowPaywall(false)}>
              <Text style={styles.closeBtnText}>✕ Skip</Text>
            </TouchableOpacity>
            <Text style={styles.paywallTitle}>YAZIO-Next PRO</Text>
            <Text style={styles.paywallSub}>
              Unbegrenzte KI-Fotos, Autophagie-Fasten & Smarte Nährwertanalyse
            </Text>
            <View style={styles.paywallPlanCard}>
              <Text style={styles.bold}>12 Monate Plan (Beliebtest)</Text>
              <Text style={styles.paywallPrice}>29,99 € / Jahr (2,49 € / Monat)</Text>
            </View>
            <TouchableOpacity
              style={styles.primaryBtn}
              onPress={() => {
                setIsProUser(true);
                setShowPaywall(false);
                Alert.alert('PRO Aktiviert', 'Vielen Dank! Alle PRO-Funktionen sind freigeschaltet.');
              }}
            >
              <Text style={styles.primaryBtnText}>Jetzt PRO aktivieren</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Spinning Wheel Modal (Screen 33: 75% OFF Downsell) */}
      <Modal visible={showSpinWheel} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <TouchableOpacity style={styles.closeBtn} onPress={() => setShowSpinWheel(false)}>
              <Text style={styles.closeBtnText}>✕ Schließen</Text>
            </TouchableOpacity>
            <Text style={styles.wheelTitle}>🎡 Dein Glücksrad</Text>
            <Text style={styles.wheelSubtitle}>
              Drehe das Rad und sichere dir bis zu 75% Rabatt!
            </Text>
            <View style={styles.discountBadge}>
              <Text style={styles.discountBadgeText}>🎉 75% RABATT FÜR IMMER GEWONNEN!</Text>
            </View>
            <Text style={styles.paywallPrice}>Nur 9,99 € für das gesamte 1. Jahr</Text>
            <TouchableOpacity
              style={styles.primaryBtn}
              onPress={() => {
                setIsProUser(true);
                setShowSpinWheel(false);
                Alert.alert('75% Rabatt Eingelöst!', 'Dein PRO-Abo zum Sonderpreis von 9,99 € ist aktiv.');
              }}
            >
              <Text style={styles.primaryBtnText}>75% Rabatt jetzt sichern</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  content: { flex: 1 },
  scroll: { padding: 16, gap: 14, paddingBottom: 30 },
  screenHeader: { fontSize: 22, fontWeight: '700', color: '#F8FAFC', marginBottom: 4 },
  dateRow: { flexDirection: 'row', gap: 8 },
  dateChip: { backgroundColor: '#1E293B', paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20 },
  activeDateChip: { backgroundColor: '#10B981' },
  dateChipText: { color: '#94A3B8', fontSize: 13, fontWeight: '600' },
  activeDateChipText: { color: '#064E3B' },
  card: { backgroundColor: '#1E293B', borderRadius: 16, padding: 16, gap: 10 },
  cardHeaderRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardTitle: { color: '#E2E8F0', fontSize: 16, fontWeight: '700' },
  badgeRow: { flexDirection: 'row', gap: 8 },
  badgeText: { color: '#FCD34D', fontSize: 12, fontWeight: '600' },
  ringContainer: { flexDirection: 'row', alignItems: 'center', gap: 16, marginTop: 4 },
  calorieCircle: {
    width: 110,
    height: 110,
    borderRadius: 55,
    borderWidth: 6,
    borderColor: '#10B981',
    alignItems: 'center',
    justifyContent: 'center',
  },
  calorieBigText: { fontSize: 26, fontWeight: '800', color: '#10B981' },
  calorieSubText: { fontSize: 11, color: '#94A3B8' },
  summaryStats: { flex: 1, gap: 2 },
  statLine: { color: '#CBD5E1', fontSize: 13 },
  bold: { fontWeight: '700', color: '#F8FAFC' },
  divider: { height: 1, backgroundColor: '#334155', marginVertical: 4 },
  macroMini: { fontSize: 11, color: '#94A3B8' },
  promoBanner: { backgroundColor: '#7C3AED', padding: 10, borderRadius: 10, alignItems: 'center' },
  promoBannerText: { color: '#EDE9FE', fontWeight: '700', fontSize: 12 },
  mealCard: { backgroundColor: '#1E293B', borderRadius: 14, padding: 14, gap: 8 },
  mealHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  mealTitle: { color: '#F8FAFC', fontSize: 15, fontWeight: '700' },
  mealTargetText: { color: '#94A3B8', fontSize: 12 },
  addMealBtn: { backgroundColor: '#334155', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8 },
  addMealBtnText: { color: '#38BDF8', fontWeight: '600', fontSize: 12 },
  foodRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingTop: 6, borderTopWidth: 1, borderTopColor: '#334155' },
  foodName: { color: '#E2E8F0', fontSize: 14, fontWeight: '500' },
  foodDetails: { color: '#64748B', fontSize: 11 },
  foodCals: { color: '#F8FAFC', fontWeight: '600', fontSize: 13 },
  glassesRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 4 },
  glassBtn: { padding: 8, backgroundColor: '#334155', borderRadius: 8 },
  glassFilled: { backgroundColor: '#0284C7' },
  glassText: { fontSize: 18 },
  mutedText: { color: '#94A3B8', fontSize: 12 },
  actionMethodsRow: { flexDirection: 'row', gap: 12 },
  methodCard: { flex: 1, backgroundColor: '#1E293B', borderRadius: 14, padding: 14, alignItems: 'center', gap: 4 },
  aiMethodCard: { borderColor: '#10B981', borderWidth: 1 },
  methodIcon: { fontSize: 24 },
  methodTitle: { color: '#F8FAFC', fontWeight: '700', fontSize: 13 },
  methodSubtitle: { color: '#10B981', fontSize: 11 },
  searchInput: { backgroundColor: '#1E293B', color: '#F8FAFC', borderRadius: 12, padding: 14, fontSize: 14 },
  sectionTitle: { color: '#94A3B8', fontSize: 13, fontWeight: '600', marginTop: 8 },
  catalogItem: { backgroundColor: '#1E293B', borderRadius: 12, padding: 14, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  catalogItemName: { color: '#F8FAFC', fontSize: 14, fontWeight: '600' },
  catalogItemPortion: { color: '#64748B', fontSize: 12 },
  catalogItemCals: { color: '#10B981', fontWeight: '700', fontSize: 14 },
  pickerCard: { backgroundColor: '#334155', borderRadius: 14, padding: 16, gap: 10 },
  pickerTitle: { color: '#F8FAFC', fontSize: 16, fontWeight: '700' },
  pickerServingText: { color: '#94A3B8', fontSize: 12 },
  gramInputRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  label: { color: '#CBD5E1', fontSize: 14 },
  gramInput: { backgroundColor: '#1E293B', color: '#F8FAFC', borderRadius: 8, padding: 8, width: 80, textAlign: 'center', fontWeight: '700' },
  foodRatingBox: { backgroundColor: '#064E3B', padding: 8, borderRadius: 8 },
  foodRatingText: { color: '#A7F3D0', fontSize: 12, fontWeight: '600' },
  primaryBtn: { backgroundColor: '#10B981', padding: 14, borderRadius: 12, alignItems: 'center' },
  primaryBtnText: { color: '#064E3B', fontWeight: '700', fontSize: 14 },
  secondaryBtn: { backgroundColor: '#334155', padding: 12, borderRadius: 10, alignItems: 'center' },
  secondaryBtnText: { color: '#38BDF8', fontWeight: '600', fontSize: 13 },
  proUpgradeBtn: { backgroundColor: '#D97706', padding: 14, borderRadius: 12, alignItems: 'center', marginTop: 8 },
  proUpgradeBtnText: { color: '#FEF3C7', fontWeight: '700', fontSize: 14 },
  fastingClock: { alignItems: 'center', paddingVertical: 16 },
  fastingBigTime: { fontSize: 32, fontWeight: '800', color: '#38BDF8' },
  fastingStatusText: { color: '#F59E0B', fontSize: 14, fontWeight: '600', marginTop: 4 },
  phasesBox: { gap: 6, marginVertical: 8 },
  phaseItem: { color: '#10B981', fontSize: 12 },
  phaseItemActive: { color: '#F59E0B', fontSize: 12, fontWeight: '700' },
  phaseItemLocked: { color: '#64748B', fontSize: 12 },
  recipeTagsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  recipeFilterChip: { backgroundColor: '#1E293B', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 16 },
  recipeFilterText: { color: '#94A3B8', fontSize: 12 },
  recipeCard: { backgroundColor: '#1E293B', borderRadius: 14, padding: 16, gap: 8 },
  recipeTitle: { color: '#F8FAFC', fontSize: 16, fontWeight: '700' },
  recipeDetails: { color: '#38BDF8', fontSize: 13 },
  bottomNav: { flexDirection: 'row', backgroundColor: '#0B1120', borderTopWidth: 1, borderTopColor: '#1E293B', paddingVertical: 8 },
  navItem: { flex: 1, alignItems: 'center', paddingVertical: 4 },
  activeNavItem: {},
  navIcon: { fontSize: 18 },
  navLabel: { fontSize: 10, color: '#64748B', marginTop: 2 },
  activeNavLabel: { color: '#10B981', fontWeight: '700' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.85)', justifyContent: 'center', padding: 20 },
  modalContent: { backgroundColor: '#1E293B', borderRadius: 20, padding: 24, gap: 14 },
  closeBtn: { alignSelf: 'flex-end', padding: 4 },
  closeBtnText: { color: '#94A3B8', fontSize: 14 },
  paywallTitle: { fontSize: 24, fontWeight: '800', color: '#F8FAFC', textAlign: 'center' },
  paywallSub: { fontSize: 13, color: '#94A3B8', textAlign: 'center' },
  paywallPlanCard: { backgroundColor: '#334155', padding: 16, borderRadius: 12, alignItems: 'center', gap: 4 },
  paywallPrice: { fontSize: 16, fontWeight: '700', color: '#10B981' },
  wheelTitle: { fontSize: 24, fontWeight: '800', color: '#F59E0B', textAlign: 'center' },
  wheelSubtitle: { fontSize: 13, color: '#94A3B8', textAlign: 'center' },
  discountBadge: { backgroundColor: '#065F46', padding: 12, borderRadius: 12, alignItems: 'center' },
  discountBadgeText: { color: '#6EE7B7', fontWeight: '800', fontSize: 14 },
});
