<template>
<div>
  <h3 class="text-3xl font-medium text-color-title">{{ $t('boats') }}</h3>

  <div class="mt-3 lg:mt-8 p-3 lg:px-6 lg:pb-6 lg:pt-4 bg-svg-image bg-blue-500 rounded-md shadow">
    <h4 class="text-color-nav">Boote Filter</h4>
    <boat-filter @resultObject="handleBoatFilter" @resetFilter="handleBoatReset" :showResetButton="true" />
  </div>

  <div v-if="boats.length > 0" class="flex flex-col mt-8">
    <div class="overflow-x-auto">
      <div class="min-w-full align-middle inline-block shadow overflow-hidden rounded">
        <table class="min-w-full">
          <thead class="bg-color-image text-gray-900">
            <tr>
              <th class="px-6 py-6 text-left text-xs leading-4 font-medium uppercase tracking-wider">
                {{ $t('name') }}
              </th>
              <th class="py-6 text-left text-xs leading-4 font-medium uppercase tracking-wider">
                {{ $t('category') }}
              </th>
              <th class="px-6 py-6 text-left text-xs leading-4 font-medium uppercase tracking-wider">
                {{ $t('steered') }}
              </th>
              <th class="px-6 py-6 text-left text-xs leading-4 font-medium uppercase tracking-wider">
                {{ $t('crewsize') }}
              </th>
              <th class="px-6 py-6 text-left text-xs leading-4 font-medium uppercase tracking-wider">
                {{ $t('discipline') }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-color-form">
            <tr v-for="(b, index) in boats" :key="index" class="border-b-2 border-gray-200">
              <td class="px-6 py-4 whitespace-no-wrap">
                <div class="flex items-center">
                  <div class="ml-4">
                    <div class="text-sm leading-5 font-medium text-gray-900">
                      {{ b.name }}
                    </div>
                    <div class="text-sm leading-5 text-color-body">
                      {{ boatCategories[b.id] }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-no-wrap text-sm leading-5 text-color-body">
                <span v-if="b.category == 0">Gig</span>
                <span v-else>Rennboot</span>
              </td>
              <td class="px-6 py-4 whitespace-no-wrap text-sm leading-5 text-color-body">
                <span v-if="b.coxswain == 0">Ja</span>
                <span v-if="b.coxswain == 1">Nein</span>
                <span v-if="b.coxswain == 2">Wechselbar</span>
                <span v-if="b.coxswain == 3">Ja (wechselbar)</span>
                <span v-if="b.coxswain == 4">Nein (wechselbar)</span>
              </td>
              <td class="px-6 py-4 whitespace-no-wrap text-sm leading-5 text-color-body">
                {{ b.crewsize }}
              </td>
              <td class="px-6 py-4 whitespace-no-wrap text-sm leading-5 text-color-body">
                <span v-if="b.coxswain == 0">Sculling</span>
                <span v-if="b.coxswain == 1">Riemen</span>
                <span v-if="b.coxswain == 2">Sculling (wechselbar)</span>
                <span v-if="b.coxswain == 3">Riemen (wechselbar)</span>
                <span v-if="b.coxswain == 4">Unbekannt</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import {
  BoatCategory
} from '@/plugins/boatcategory'

export default {
  data() {
    return {
      boats: [],
      boatCategories: {},
      boatsBackup: []
    }
  },
  mounted() {
    this.$axios({
      method: 'GET',
      url: `${process.env.API_URL}/boats`,
      validateStatus: () => true
    }).then((res) => {
      if (res.status === 200) {
        this.boats = res.data
        this.boatsBackup = res.data
        this.boatCategories = BoatCategory.getCategories(res.data)
      } else {
        console.debug(res.data)
      }
    })
  },
  methods: {
    handleBoatFilter(value) {
      this.boats = [value.boat]
    },
    handleBoatReset(value) {
      if (value === true) {
        this.boats = this.boatsBackup
      }
    }
  }
}
</script>