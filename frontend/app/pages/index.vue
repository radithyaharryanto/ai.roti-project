<template>
  <div class="fixed w-full h-full">
    <div class="relative w-full h-full flex">
      
      <!-- ROI FORM container -->
      <div class="p-10 text-black relative overflow-y-auto transition-all duration-700 ease-in-out" :class="hasResult ? 'w-1/2' : 'w-full'">
        <h1 class="font-bold">
          Welcome to Astra Gen AI ROI
        </h1>
        <p class="text-gray-500">
          Please fill out all the field to get the insight, make sure the value are based on calculation from ROI
        </p>

        <form class="mt-8 space-y-6 pb-10" @submit="handleSubmit">
          <div class="grid grid-cols-2 gap-6">
            
            <!-- Unit Name -->
            <fieldset class="fieldset col-span-2">
              <legend class="fieldset-legend">
                Unit Name <span class="text-error">*</span>
              </legend>
              <input v-model="inputData.unit_name" type="text" placeholder="e.g Truck ABC" class="input input-bordered w-full" :class="{ 'input-error': errors.unit_name }" aria-label="Unit Name">
              <div v-if="errors.unit_name" class="label">
                <span class="label-text-alt text-error">{{ errors.unit_name }}</span>
              </div>
            </fieldset>

            <!-- Unit Price -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Unit Price (Rp) <span class="text-error">*</span>
              </legend>
              <input type="text" placeholder="e.g 12,000,000" class="input input-bordered w-full" :class="{ 'input-error': errors.unit_price }" aria-label="Unit Price" :value="formattedUnitPrice" @input="handleNumberInput('unit_price', $event)">
              <div v-if="errors.unit_price" class="label">
                <span class="label-text-alt text-error">{{ errors.unit_price }}</span>
              </div>
            </fieldset>

            <!-- Segment -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Segment <span class="text-error">*</span>
              </legend>
              <select v-model="inputData.segment" class="select select-bordered w-full" :class="{ 'select-error': errors.segment }" aria-label="Segment">
                <option disabled selected value="">
                  --Select Segment--
                </option>
                <option>Segment A</option>
                <option>Segment B</option>
                <option>Segment C</option>
              </select>
              <div v-if="errors.segment" class="label">
                <span class="label-text-alt text-error">{{ errors.segment }}</span>
              </div>
            </fieldset>

            <!-- Uses Leasing -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Uses Leasing?
              </legend>
              <select v-model="inputData.uses_leasing" class="select select-bordered w-full" aria-label="Uses Leasing">
                <option disabled selected value="">
                  --Select Option--
                </option>
                <option value="true">
                  Yes
                </option>
                <option value="false">
                  No
                </option>
              </select>
            </fieldset>

            <!-- Total Cost of Ownership (TCO) -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Total Cost of Ownership (TCO) <span class="text-error">*</span>
              </legend>
              <input type="text" placeholder="e.g 250,000,000" class="input input-bordered w-full" :class="{ 'input-error': errors.tco }" aria-label="Total Cost of Ownership" :value="formattedTco" @input="handleNumberInput('tco', $event)">
              <div v-if="errors.tco" class="label">
                <span class="label-text-alt text-error">{{ errors.tco }}</span>
              </div>
            </fieldset>

            <!-- Annual TCO -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Annual TCO (Rp) <span class="text-error">*</span>
              </legend>
              <input type="text" placeholder="e.g 25,000,000" class="input input-bordered w-full" :class="{ 'input-error': errors.annual_tco }" aria-label="Annual TCO" :value="formattedAnnualTco" @input="handleNumberInput('annual_tco', $event)">
              <div v-if="errors.annual_tco" class="label">
                <span class="label-text-alt text-error">{{ errors.annual_tco }}</span>
              </div>
            </fieldset>

            <!-- Cost per KM -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Cost per KM (Rp) <span class="text-error">*</span>
              </legend>
              <input type="text" placeholder="e.g 500,000" class="input input-bordered w-full" :class="{ 'input-error': errors.cost_per_km }" aria-label="Cost per KM" :value="formattedCostPerKm" @input="handleNumberInput('cost_per_km', $event)">
              <div v-if="errors.cost_per_km" class="label">
                <span class="label-text-alt text-error">{{ errors.cost_per_km }}</span>
              </div>
            </fieldset>

            <!-- Revenue per KM -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Revenue per KM (Rp) <span class="text-error">*</span>
              </legend>
              <input type="text" placeholder="e.g 8,000" class="input input-bordered w-full" :class="{ 'input-error': errors.revenue_per_km }" aria-label="Revenue per KM" :value="formattedRevenuePerKm" @input="handleNumberInput('revenue_per_km', $event)">
              <div v-if="errors.revenue_per_km" class="label">
                <span class="label-text-alt text-error">{{ errors.revenue_per_km }}</span>
              </div>
            </fieldset>

            <!-- Contribution Margin -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Contribution Margin (Rp) <span class="text-error">*</span>
              </legend>
              <input type="text" placeholder="e.g 5,700" class="input input-bordered w-full" :class="{ 'input-error': errors.contribution_margin }" aria-label="Contribution Margin" :value="formattedContributionMargin" @input="handleNumberInput('contribution_margin', $event)">
              <div v-if="errors.contribution_margin" class="label">
                <span class="label-text-alt text-error">{{ errors.contribution_margin }}</span>
              </div>
            </fieldset>

            <!-- Total Revenue -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Total Revenue (Rp) <span class="text-error">*</span>
              </legend>
              <input type="text" placeholder="e.g 500,000" class="input input-bordered w-full" :class="{ 'input-error': errors.total_revenue }" aria-label="Total Revenue" :value="formattedTotalRevenue" @input="handleNumberInput('total_revenue', $event)">
              <div v-if="errors.total_revenue" class="label">
                <span class="label-text-alt text-error">{{ errors.total_revenue }}</span>
              </div>
            </fieldset>

            <!-- ROI Ratio -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                ROI Ratio <span class="text-error">*</span>
              </legend>
              <input type="text" placeholder="e.g 1.06" class="input input-bordered w-full" :class="{ 'input-error': errors.roi }" aria-label="ROI Ratio" :value="formattedRoi" @input="handleDecimalInput('roi', $event)">
              <div v-if="errors.roi" class="label">
                <span class="label-text-alt text-error">{{ errors.roi }}</span>
              </div>
            </fieldset>

            <!-- Break-even Point (Years) -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Break-even Point (Years) <span class="text-error">*</span>
              </legend>
              <input type="text" placeholder="e.g 3.5" class="input input-bordered w-full" :class="{ 'input-error': errors.bep_years }" aria-label="Break-even Point Years" :value="formattedBepYears" @input="handleDecimalInput('bep_years', $event)">
              <div v-if="errors.bep_years" class="label">
                <span class="label-text-alt text-error">{{ errors.bep_years }}</span>
              </div>
            </fieldset>

            <!-- Break-even Point (KM) -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Break-even Point (KM) <span class="text-error">*</span>
              </legend>
              <input type="text" placeholder="e.g 1,200,000" class="input input-bordered w-full" :class="{ 'input-error': errors.bep_km }" aria-label="Break-even Point KM" :value="formattedBepKm" @input="handleNumberInput('bep_km', $event)">
              <div v-if="errors.bep_km" class="label">
                <span class="label-text-alt text-error">{{ errors.bep_km }}</span>
              </div>
            </fieldset>

            <!-- Owning Cost -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Owning Cost (%)
              </legend>
              <input type="text" placeholder="e.g 0.56" class="input input-bordered w-full" :class="{ 'input-error': errors.owning_pct }" aria-label="Owning Cost" :value="formattedOwningPct" @input="handleDecimalInput('owning_pct', $event)">
              <div v-if="errors.owning_pct" class="label">
                <span class="label-text-alt text-error">{{ errors.owning_pct }}</span>
              </div>
            </fieldset>

            <!-- Operational Cost -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Operational Cost (%)
              </legend>
              <input type="text" placeholder="e.g 0.44" class="input input-bordered w-full" :class="{ 'input-error': errors.operational_pct }" aria-label="Operational Cost" :value="formattedOperationalPct" @input="handleDecimalInput('operational_pct', $event)">
              <div v-if="errors.operational_pct" class="label">
                <span class="label-text-alt text-error">{{ errors.operational_pct }}</span>
              </div>
            </fieldset>

            <!-- Residual Value -->
            <fieldset class="fieldset">
              <legend class="fieldset-legend">
                Residual Value (%)
              </legend>
              <input type="text" placeholder="e.g 0.30" class="input input-bordered w-full" :class="{ 'input-error': errors.residual_value_pct }" aria-label="Residual Value" :value="formattedResidualValuePct" @input="handleDecimalInput('residual_value_pct', $event)">
              <div v-if="errors.residual_value_pct" class="label">
                <span class="label-text-alt text-error">{{ errors.residual_value_pct }}</span>
              </div>
            </fieldset>

          </div>

          <!-- Submit Button -->
          <div class="mt-8 flex justify-center gap-4 w-full">
            <button type="button" class="btn btn-outline btn-secondary" @click="fillTestData">
              Fill Test Data
            </button>
            <button type="button" class="btn btn-soft btn-primary" @click="handleClear">
              Clear Value
            </button>
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="loading loading-spinner loading-sm" />
              {{ isSubmitting ? 'Calculating...' : 'Calculate ROI' }}
            </button>
          </div>
        </form>
      </div>
      
      <!-- analisys result container -->
      <div class="h-full bg-white shadow-md relative overflow-y-auto transition-all duration-700 ease-in-out" :class="(hasResult || isSubmitting) ? 'w-1/2 p-10 opacity-100' : 'w-0 p-0 opacity-0 overflow-hidden'">
        
        <!-- Loading State -->
        <div v-if="isSubmitting && !hasResult" class="flex flex-col items-center justify-center h-full">
          <div class="loading loading-spinner loading-lg text-primary mb-4" />
          <h3 class="text-xl font-bold text-blue-900 mb-2">Analyzing Your Data...</h3>
          <p class="text-gray-600 text-center">AI sedang menganalisis data kendaraan Anda</p>
        </div>

        <!-- Results -->
        <div v-if="hasResult && resultData" ref="resultsContainer">
          <h2 class="font-bold text-xl mb-4 text-blue-900">
            📊 Hasil Analisis ROI
          </h2>
          
          <!-- Summary Card -->
          <div class="p-4 border-2 border-blue-200 rounded-lg bg-gradient-to-r from-blue-50 to-blue-100 mb-4">
            <h3 class="font-bold text-blue-900 mb-2 text-lg">
              {{ resultData.unit_name }}
            </h3>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span class="text-gray-700 font-medium">Segment:</span>
                <span class="font-semibold ml-2">{{ resultData.segment }}</span>
              </div>
              <div>
                <span class="text-gray-700 font-medium">Leasing:</span>
                <span class="font-semibold ml-2">{{ resultData.uses_leasing ? 'Ya' : 'Tidak' }}</span>
              </div>
            </div>
          </div>

          <div class="space-y-4">
            <!-- ROI Analysis -->
            <div v-if="resultData.roi" class="p-4 border rounded-lg" :class="getCategoryColor(resultData.roi.category)">
              <h3 class="font-bold text-lg mb-2 flex items-center gap-2">
                <span>💰</span>
                <span>ROI Analysis</span>
              </h3>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between items-center">
                  <span class="text-gray-700">ROI:</span>
                  <span class="font-bold text-lg">{{ resultData.roi.percentage }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-700">Kategori:</span>
                  <span class="px-3 py-1 rounded-full font-semibold text-sm" :class="getCategoryBadge(resultData.roi.category)">
                    {{ resultData.roi.category }}
                  </span>
                </div>
                <div v-if="resultData.roi.short_sentence" class="mt-2">
                  <p class="text-gray-800 font-medium">{{ resultData.roi.short_sentence }}</p>
                </div>
                <div v-if="resultData.roi.insight_narrative" class="mt-2">
                  <p class="text-gray-700 leading-relaxed">{{ resultData.roi.insight_narrative }}</p>
                </div>
              </div>
            </div>

            <!-- TCO Analysis -->
            <div v-if="resultData.tco" class="p-4 border rounded-lg bg-purple-50 border-purple-200">
              <h3 class="font-bold text-lg mb-2 flex items-center gap-2">
                <span>📈</span>
                <span>TCO Analysis</span>
              </h3>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-700">Biaya per KM:</span>
                  <span class="font-semibold">{{ resultData.tco.amount_rp }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-700">Efisiensi:</span>
                  <span class="px-3 py-1 rounded-full font-semibold text-sm bg-purple-200 text-purple-900">
                    {{ resultData.tco.category }}
                  </span>
                </div>
                <div v-if="resultData.tco.short_sentence" class="mt-2">
                  <p class="text-gray-800 font-medium">{{ resultData.tco.short_sentence }}</p>
                </div>
                <div v-if="resultData.tco.insight_narrative" class="mt-2">
                  <p class="text-gray-700 leading-relaxed">{{ resultData.tco.insight_narrative }}</p>
                </div>
              </div>
            </div>

            <!-- Owning vs Operational Costs -->
            <div v-if="resultData.owning_vs_operational" class="p-4 border rounded-lg bg-orange-50 border-orange-200">
              <h3 class="font-bold text-lg mb-2 flex items-center gap-2">
                <span>🔄</span>
                <span>Struktur Biaya</span>
              </h3>
              <div class="space-y-3 text-sm">
                <div class="space-y-1">
                  <div class="flex justify-between">
                    <span class="text-gray-700">Owning Cost:</span>
                    <span class="font-semibold">{{ resultData.owning_vs_operational.owning_percentage }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-orange-500 h-2 rounded-full" :style="{ width: resultData.owning_vs_operational.owning_percentage + '%' }" />
                  </div>
                </div>
                <div class="space-y-1">
                  <div class="flex justify-between">
                    <span class="text-gray-700">Operational Cost:</span>
                    <span class="font-semibold">{{ resultData.owning_vs_operational.operational_percentage }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-blue-500 h-2 rounded-full" :style="{ width: resultData.owning_vs_operational.operational_percentage + '%' }" />
                  </div>
                </div>
                <div class="flex justify-between items-center mt-2">
                  <span class="text-gray-700">Kategori:</span>
                  <span class="px-3 py-1 rounded-full font-semibold text-sm bg-orange-200 text-orange-900">
                    {{ resultData.owning_vs_operational.category }}
                  </span>
                </div>
                <div v-if="resultData.owning_vs_operational.short_sentence" class="mt-2">
                  <p class="text-gray-800 font-medium">{{ resultData.owning_vs_operational.short_sentence }}</p>
                </div>
                <div v-if="resultData.owning_vs_operational.cashflow_implication" class="mt-2">
                  <p class="text-gray-700 leading-relaxed">{{ resultData.owning_vs_operational.cashflow_implication }}</p>
                </div>
              </div>
            </div>

            <!-- Break-Even Point -->
            <div v-if="resultData.break_even_point" class="p-4 border rounded-lg bg-teal-50 border-teal-200">
              <h3 class="font-bold text-lg mb-2 flex items-center gap-2">
                <span>⏱️</span>
                <span>Break-Even Point</span>
              </h3>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-700">Periode BEP:</span>
                  <span class="font-semibold">{{ resultData.break_even_point.period }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-700">BEP (KM):</span>
                  <span class="font-semibold">{{ resultData.break_even_point.bep_km }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-700">Kategori:</span>
                  <span class="px-3 py-1 rounded-full font-semibold text-sm bg-teal-200 text-teal-900">
                    {{ resultData.break_even_point.category }}
                  </span>
                </div>
                <div v-if="resultData.break_even_point.short_sentence" class="mt-2">
                  <p class="text-gray-800 font-medium">{{ resultData.break_even_point.short_sentence }}</p>
                </div>
                
                <!-- Monthly Simulation -->
                <div v-if="resultData.break_even_point.monthly_simulation" class="mt-3 p-3 bg-teal-100 rounded-lg">
                  <h4 class="font-semibold text-teal-900 mb-2">Simulasi Bulanan</h4>
                  <div class="space-y-1">
                    <div class="flex justify-between">
                      <span class="text-teal-800">Cicilan:</span>
                      <span class="font-semibold text-teal-900">{{ resultData.break_even_point.monthly_simulation.installment }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-teal-800">Revenue:</span>
                      <span class="font-semibold text-teal-900">{{ resultData.break_even_point.monthly_simulation.revenue }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-teal-800">Net Cashflow:</span>
                      <span class="font-semibold text-teal-900">{{ resultData.break_even_point.monthly_simulation.net_cashflow }}</span>
                    </div>
                  </div>
                </div>
                
                <div v-if="resultData.break_even_point.bep_insight" class="mt-2">
                  <p class="text-gray-700 leading-relaxed">{{ resultData.break_even_point.bep_insight }}</p>
                </div>
              </div>
            </div>

            <!-- Contribution Margin -->
            <div v-if="resultData.contribution_margin_per_km" class="p-4 border rounded-lg bg-indigo-50 border-indigo-200">
              <h3 class="font-bold text-lg mb-2 flex items-center gap-2">
                <span>💵</span>
                <span>Contribution Margin</span>
              </h3>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-700">Margin per KM:</span>
                  <span class="font-semibold">{{ resultData.contribution_margin_per_km.margin_rp }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-700">Kategori:</span>
                  <span class="px-3 py-1 rounded-full font-semibold text-sm bg-indigo-200 text-indigo-900">
                    {{ resultData.contribution_margin_per_km.category }}
                  </span>
                </div>
                <div v-if="resultData.contribution_margin_per_km.short_sentence" class="mt-2">
                  <p class="text-gray-800 font-medium">{{ resultData.contribution_margin_per_km.short_sentence }}</p>
                </div>
                <div v-if="resultData.contribution_margin_per_km.margin_insight" class="mt-2">
                  <p class="text-gray-700 leading-relaxed">{{ resultData.contribution_margin_per_km.margin_insight }}</p>
                </div>
              </div>
            </div>

            <!-- Overall Insight (AI Generated) -->
            <div v-if="resultData.overall_insight" class="p-4 border-2 border-green-300 rounded-lg bg-gradient-to-br from-green-50 to-emerald-50">
              <h3 class="font-bold text-lg mb-3 flex items-center gap-2 text-green-900">
                <span>🤖</span>
                <span>AI-Powered Insights</span>
              </h3>
              <div class="prose prose-sm max-w-none">
                <p class="text-gray-800 leading-relaxed whitespace-pre-line">{{ resultData.overall_insight.summary }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    
    </div>

    <!-- Modal Dialog -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="closeModal">
      <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" />
      <div class="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6 animate-fade-in" @click.stop>
        <!-- Modal Header -->
        <div class="flex items-start justify-between mb-4">
          <h3 class="text-xl font-bold" :class="modalConfig.type === 'alert' ? 'text-red-600' : 'text-blue-600'">
            {{ modalConfig.title }}
          </h3>
          <button class="btn btn-sm btn-circle btn-ghost" @click="closeModal">
            ✕
          </button>
        </div>
        
        <!-- Modal Body -->
        <div class="mb-6">
          <p class="text-gray-700 whitespace-pre-line">{{ modalConfig.message }}</p>
        </div>
        
        <!-- Modal Actions -->
        <div class="flex justify-end gap-3">
          <button v-if="modalConfig.type === 'confirm'" class="btn btn-ghost" @click="closeModal">
            {{ modalConfig.cancelText }}
          </button>
          <button class="btn" :class="modalConfig.type === 'alert' ? 'btn-primary' : 'btn-error'" @click="handleModalConfirm">
            {{ modalConfig.confirmText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { gsap } from 'gsap'

definePageMeta({
  layout: 'main'
})

useSeoMeta({
  ogUrl: '',
  title: 'ROI AI Analysis',
  ogTitle: 'ROI AI Analysis',
  twitterTitle: 'ROI AI Analysis',
  description: 'Calculate your ROI with AI and get analytical insights to optimize your investments.',
  ogDescription: 'Calculate your ROI with AI and get analytical insights to optimize your investments.',
  twitterDescription: 'Calculate your ROI with AI and get analytical insights to optimize your investments.',
  ogType: 'website',
  twitterCard: 'summary',
})

// Form data
const inputData = ref({
  unit_name: '',
  unit_price: '',
  segment: '',
  uses_leasing: 'false', // default to false
  tco: '',
  annual_tco: '',
  cost_per_km: '',
  revenue_per_km: '',
  contribution_margin: '',
  total_revenue: '',
  roi: '',
  bep_years: '',
  bep_km: '',
  owning_pct: '',
  operational_pct: '',
  residual_value_pct: '0.30' // default to 0.30
})

// Validation errors
const errors = ref({})
const isSubmitting = ref(false)
const hasResult = ref(false)
const resultData = ref(null)
const resultsContainer = ref(null)

// Modal state
const showModal = ref(false)
const modalConfig = ref({
  type: 'alert', // 'alert' or 'confirm'
  title: '',
  message: '',
  onConfirm: null,
  confirmText: 'OK',
  cancelText: 'Cancel'
})

// Formatting functions
const formatNumber = (value) => {
  if (!value) return ''
  const num = value.toString().replace(/,/g, '')
  return num.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const formatDecimal = (value) => {
  if (!value) return ''
  return value.toString()
}

// Category color helpers
const getCategoryColor = (category) => {
  const categoryColors = {
    'Sangat Layak': 'bg-green-50 border-green-200',
    'Layak': 'bg-green-50 border-green-200',
    'Perlu Dievaluasi': 'bg-yellow-50 border-yellow-200',
    'Tidak Disarankan': 'bg-orange-50 border-orange-200',
    'Rugi': 'bg-red-50 border-red-200'
  }
  return categoryColors[category] || 'bg-gray-50 border-gray-200'
}

const getCategoryBadge = (category) => {
  const categoryBadges = {
    'Sangat Layak': 'bg-green-200 text-green-900',
    'Layak': 'bg-green-200 text-green-900',
    'Perlu Dievaluasi': 'bg-yellow-200 text-yellow-900',
    'Tidak Disarankan': 'bg-orange-200 text-orange-900',
    'Rugi': 'bg-red-200 text-red-900'
  }
  return categoryBadges[category] || 'bg-gray-200 text-gray-900'
}

// Modal helpers
const showAlert = (title, message) => {
  modalConfig.value = {
    type: 'alert',
    title,
    message,
    onConfirm: null,
    confirmText: 'OK',
    cancelText: 'Cancel'
  }
  showModal.value = true
}

const showConfirm = (title, message, onConfirm) => {
  modalConfig.value = {
    type: 'confirm',
    title,
    message,
    onConfirm,
    confirmText: 'Yes',
    cancelText: 'No'
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const handleModalConfirm = () => {
  if (modalConfig.value.onConfirm) {
    modalConfig.value.onConfirm()
  }
  closeModal()
}

// GSAP Animation for results
const animateResults = () => {
  nextTick(() => {
    if (!resultsContainer.value) return
    
    // Animate header
    gsap.from(resultsContainer.value.querySelector('h2'), {
      duration: 0.6,
      y: -30,
      opacity: 0,
      ease: 'power3.out'
    })
    
    // Animate summary card
    const summaryCard = resultsContainer.value.querySelectorAll('.p-4.border-2.border-blue-200')
    gsap.from(summaryCard, {
      duration: 0.6,
      y: 20,
      opacity: 0,
      delay: 0.2,
      ease: 'power3.out'
    })
    
    // Animate all analysis cards
    const cards = resultsContainer.value.querySelectorAll('.space-y-4 > div')
    gsap.from(cards, {
      duration: 0.7,
      y: 40,
      opacity: 0,
      stagger: 0.1,
      delay: 0.4,
      ease: 'power3.out'
    })
    
    // Animate progress bars
    const progressBars = resultsContainer.value.querySelectorAll('.bg-orange-500, .bg-blue-500')
    progressBars.forEach((bar) => {
      gsap.from(bar, {
        duration: 1.2,
        width: '0%',
        delay: 0.8,
        ease: 'power2.out'
      })
    })
  })
}

// Computed formatted values
const formattedUnitPrice = computed(() => formatNumber(inputData.value.unit_price))
const formattedTco = computed(() => formatNumber(inputData.value.tco))
const formattedAnnualTco = computed(() => formatNumber(inputData.value.annual_tco))
const formattedCostPerKm = computed(() => formatNumber(inputData.value.cost_per_km))
const formattedRevenuePerKm = computed(() => formatNumber(inputData.value.revenue_per_km))
const formattedContributionMargin = computed(() => formatNumber(inputData.value.contribution_margin))
const formattedTotalRevenue = computed(() => formatNumber(inputData.value.total_revenue))
const formattedRoi = computed(() => formatDecimal(inputData.value.roi))
const formattedBepYears = computed(() => formatDecimal(inputData.value.bep_years))
const formattedBepKm = computed(() => formatNumber(inputData.value.bep_km))
const formattedOwningPct = computed(() => formatDecimal(inputData.value.owning_pct))
const formattedOperationalPct = computed(() => formatDecimal(inputData.value.operational_pct))
const formattedResidualValuePct = computed(() => formatDecimal(inputData.value.residual_value_pct))

// Handle input changes
const handleNumberInput = (field, event) => {
  const value = event.target.value.replace(/,/g, '')
  if (value === '' || !isNaN(value)) {
    inputData.value[field] = value
    // Clear error when user types
    if (errors.value[field]) {
      const { [field]: _, ...rest } = errors.value
      errors.value = rest
    }
  }
}

const handleDecimalInput = (field, event) => {
  const value = event.target.value
  if (value === '' || /^\d*\.?\d*$/.test(value)) {
    inputData.value[field] = value
    // Clear error when user types
    if (errors.value[field]) {
      const { [field]: _, ...rest } = errors.value
      errors.value = rest
    }
  }
}

// Validation functions
const validateField = (field, value, label, options = {}) => {
  const { required = false, positive = false, range = null } = options
  
  if (required && (!value || value === '')) {
    return `${label} is required`
  }
  
  if (value && positive) {
    const numValue = parseFloat(value)
    if (numValue <= 0) {
      return `${label} must be positive`
    }
  }
  
  if (value && range) {
    const numValue = parseFloat(value)
    if (numValue < range.min || numValue > range.max) {
      return `${label} must be between ${range.min} and ${range.max}`
    }
  }
  
  return null
}

const validateForm = () => {
  const newErrors = {}
  
  // Unit Name (required)
  const unitNameError = validateField('unit_name', inputData.value.unit_name, 'Unit Name', { required: true })
  if (unitNameError) newErrors.unit_name = unitNameError
  
  // Segment (required)
  const segmentError = validateField('segment', inputData.value.segment, 'Segment', { required: true })
  if (segmentError) newErrors.segment = segmentError
  
  // Unit Price (required, positive)
  const unitPriceError = validateField('unit_price', inputData.value.unit_price, 'Unit Price', { required: true, positive: true })
  if (unitPriceError) newErrors.unit_price = unitPriceError
  
  // TCO (required, positive)
  const tcoError = validateField('tco', inputData.value.tco, 'Total Cost of Ownership', { required: true, positive: true })
  if (tcoError) newErrors.tco = tcoError
  
  // Annual TCO (required, positive)
  const annualTcoError = validateField('annual_tco', inputData.value.annual_tco, 'Annual TCO', { required: true, positive: true })
  if (annualTcoError) newErrors.annual_tco = annualTcoError
  
  // Cost per KM (required, positive)
  const costPerKmError = validateField('cost_per_km', inputData.value.cost_per_km, 'Cost per KM', { required: true, positive: true })
  if (costPerKmError) newErrors.cost_per_km = costPerKmError
  
  // Revenue per KM (required, positive)
  const revenuePerKmError = validateField('revenue_per_km', inputData.value.revenue_per_km, 'Revenue per KM', { required: true, positive: true })
  if (revenuePerKmError) newErrors.revenue_per_km = revenuePerKmError
  
  // Contribution Margin (required, positive)
  const contributionMarginError = validateField('contribution_margin', inputData.value.contribution_margin, 'Contribution Margin', { required: true, positive: true })
  if (contributionMarginError) newErrors.contribution_margin = contributionMarginError
  
  // Total Revenue (required, positive)
  const totalRevenueError = validateField('total_revenue', inputData.value.total_revenue, 'Total Revenue', { required: true, positive: true })
  if (totalRevenueError) newErrors.total_revenue = totalRevenueError
  
  // ROI (required, positive)
  const roiError = validateField('roi', inputData.value.roi, 'ROI Ratio', { required: true, positive: true })
  if (roiError) newErrors.roi = roiError
  
  // BEP Years (required, positive)
  const bepYearsError = validateField('bep_years', inputData.value.bep_years, 'Break-even Point (Years)', { required: true, positive: true })
  if (bepYearsError) newErrors.bep_years = bepYearsError
  
  // BEP KM (required, positive)
  const bepKmError = validateField('bep_km', inputData.value.bep_km, 'Break-even Point (KM)', { required: true, positive: true })
  if (bepKmError) newErrors.bep_km = bepKmError
  
  // Owning Cost % (optional, 0-1)
  if (inputData.value.owning_pct) {
    const owningPctError = validateField('owning_pct', inputData.value.owning_pct, 'Owning Cost %', { range: { min: 0, max: 1 } })
    if (owningPctError) newErrors.owning_pct = owningPctError
  }
  
  // Operational Cost % (optional, 0-1)
  if (inputData.value.operational_pct) {
    const operationalPctError = validateField('operational_pct', inputData.value.operational_pct, 'Operational Cost %', { range: { min: 0, max: 1 } })
    if (operationalPctError) newErrors.operational_pct = operationalPctError
  }
  
  // Residual Value % (optional, 0-1)
  if (inputData.value.residual_value_pct) {
    const residualValuePctError = validateField('residual_value_pct', inputData.value.residual_value_pct, 'Residual Value %', { range: { min: 0, max: 1 } })
    if (residualValuePctError) newErrors.residual_value_pct = residualValuePctError
  }
  
  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

// Clear form
const clearForm = () => {
  inputData.value = {
    unit_name: '',
    unit_price: '',
    segment: '',
    uses_leasing: 'false',
    tco: '',
    annual_tco: '',
    cost_per_km: '',
    revenue_per_km: '',
    contribution_margin: '',
    total_revenue: '',
    roi: '',
    bep_years: '',
    bep_km: '',
    owning_pct: '',
    operational_pct: '',
    residual_value_pct: '0.30'
  }
  errors.value = {}
  
  // Fade out before clearing
  if (resultsContainer.value) {
    gsap.to(resultsContainer.value, {
      duration: 0.3,
      opacity: 0,
      onComplete: () => {
        hasResult.value = false
        resultData.value = null
      }
    })
  } else {
    hasResult.value = false
    resultData.value = null
  }
}

// Submit form
const handleSubmit = async (event) => {
  event.preventDefault()
  
  if (!validateForm()) {
    // Scroll to first error
    const firstErrorField = Object.keys(errors.value)[0]
    const errorElement = document.querySelector(`[aria-label*="${firstErrorField}"]`)
    if (errorElement) {
      errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
    return
  }
  
  isSubmitting.value = true
  
  try {
    // Prepare data for backend
    const submitData = {
      unit_name: inputData.value.unit_name,
      segment: inputData.value.segment,
      unit_price: parseFloat(inputData.value.unit_price),
      uses_leasing: inputData.value.uses_leasing === 'true',
      tco: parseFloat(inputData.value.tco),
      annual_tco: parseFloat(inputData.value.annual_tco),
      cost_per_km: parseFloat(inputData.value.cost_per_km),
      revenue_per_km: parseFloat(inputData.value.revenue_per_km),
      contribution_margin: parseFloat(inputData.value.contribution_margin),
      total_revenue: parseFloat(inputData.value.total_revenue),
      roi: parseFloat(inputData.value.roi),
      bep_years: parseFloat(inputData.value.bep_years),
      bep_km: parseFloat(inputData.value.bep_km),
      owning_pct: inputData.value.owning_pct ? parseFloat(inputData.value.owning_pct) : 0.0,
      operational_pct: inputData.value.operational_pct ? parseFloat(inputData.value.operational_pct) : 0.0,
      residual_value_pct: inputData.value.residual_value_pct ? parseFloat(inputData.value.residual_value_pct) : 0.30
    }
    
    console.log('Submitting data:', submitData)
    
    // Call Flask backend API through Nuxt proxy
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(submitData)
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.error || errorData.message || `HTTP ${response.status}`)
    }
    
    const result = await response.json()
    console.log('API Response:', result)
    
    // Set result data - the response IS the analysis directly
    resultData.value = {
      ...submitData,
      ...result
    }
    hasResult.value = true
    
    // Animate results
    animateResults()
    
  } catch (error) {
    console.error('Submission error:', error)
    console.error('Error details:', {
      message: error.message,
      stack: error.stack,
      name: error.name
    })
    
    // Show more specific error message
    let errorMessage = 'An error occurred while submitting the form.'
    
    if (error.message) {
      errorMessage = error.message
    }
    
    // Check if it's a network/connection error
    if (error.message.includes('fetch') || 
        error.message.includes('Failed to fetch') ||
        error.message.includes('NetworkError') ||
        error.name === 'TypeError') {
      errorMessage = 'Cannot connect to the backend server. Please check:\n' +
                     '1. Flask server is running at http://127.0.0.1:8501\n' +
                     '2. CORS is properly configured\n' +
                     '3. Check browser console for more details'
    }
    
    showAlert('Error', errorMessage)
  } finally {
    isSubmitting.value = false
  }
}

// Clear button handler
const handleClear = (event) => {
  event.preventDefault()
  showConfirm(
    'Clear All Fields',
    'Are you sure you want to clear all fields?',
    clearForm
  )
}

// Fill test data
const fillTestData = (event) => {
  event.preventDefault()
  inputData.value = {
    unit_name: 'Truck ABC',
    unit_price: '12000000',
    segment: 'Segment A',
    uses_leasing: 'false',
    tco: '250000000',
    annual_tco: '25000000',
    cost_per_km: '500000',
    revenue_per_km: '8000',
    contribution_margin: '5700',
    total_revenue: '500000',
    roi: '1.06',
    bep_years: '3.5',
    bep_km: '1200000',
    owning_pct: '0.56',
    operational_pct: '0.44',
    residual_value_pct: '0.30'
  }
  errors.value = {}
}

// const mainStore = useMainStore()
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.2s ease-out;
}
</style>