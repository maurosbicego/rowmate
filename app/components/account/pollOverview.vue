<template>
<div>
  <h3 class="text-xl sm:text-2xl md:text-3xl font-medium leading-none text-color-title">Umfagen</h3>

  <div class="bg-svg-image bg-blue-500 rounded shadow p-3 lg:p-6 my-3 lg:my-6 mb-3">
    <h4 class="text-color-nav leading-none">Umfrage Filter</h4>
    <question-filter @resultObject="handleFilterObject" @resetFilter="handleResetValue" :borderSettings="false" />
  </div>

  <form @submit.prevent="submitForm" class="bg-color-form rounded shadow p-3 lg:p-6 mt-1 sm:mt-3 md:mt-5 lg:mt-8">
    <question-form v-if="questions.length > 0" v-for="value, index in questions" :key="value._id" @resultObject="handleFormObject($event, index)" :formObject="value" class="mb-3 lg:mb-6" />

    <div class="flex justify-end">
      <button @click="addPollForm" class="bg-color-button text-color-button rounded focus:outline-none px-4 py-2">
        {{ questions.length === 0 ? 'Frage erstellen' : 'Frage hinzufügen'}}
      </button>
      <button v-if="questions.length > 0" class="bg-blue-600 text-color-button rounded focus:outline-none px-4 py-2 ml-3">
        {{ $t('save') }}
      </button>
    </div>
  </form>

  <vote-form v-if="questions.length <= 0" @deletePollId="deletePoll" @pollObject="handlePollsObject" class="mt-1 sm:mt-3 md:mt-5 lg:mt-8" />
</div>
</template>

<script>
import {
  parse as uuidParse
} from 'uuid'

export default {
  data() {
    return {
      questions: []
    }
  },
  computed: {
    currentLocale() {
      return this.$i18n.locale
    }
  },
  methods: {
    handleResetValue(value) {
      if (value === true) {
        this.questions = []
      }
    },
    handleFilterObject(value) {
      this.questions = [value]
    },
    handleFormObject(value, index) {
      this.questions[index] = value
    },
    addPollForm(value) {
      this.questions.push({
        question: null,
        type: 'select',
        forms: [{
          id: 'option0',
          value: null
        }]
      })
    },
    buf2hex(buffer) {
      const byteArray = new Uint8Array(buffer)
      const hexParts = []

      for (let i = 0; i < byteArray.length; i++) {
        const hex = byteArray[i].toString(16)
        const paddedHex = ('00' + hex).slice(-2)
        hexParts.push(paddedHex)
      }

      return hexParts.join('')
    },
    handlePollsObject(value) {
      this.questions = value
    },
    deletePoll(value) {
      let uuid = null

      try {
        uuid = this.buf2hex(uuidParse(value))
      } catch (e) {
        console.debug(e)
      }

      this.$axios({
        method: 'DELETE',
        url: `${process.env.API_URL}/poll/${uuid}`,
        validateStatus: () => true
      }).then((res) => {
        if (res.status === 200 && res.data === true) {
          console.debug(res.data)
        } else {
          console.debug(res.data)
        }
      })
    },
    submitForm() {
      try {
        const uuid = this.buf2hex(uuidParse(this._id))

        this.$axios({
          method: 'PATCH',
          url: `${process.env.API_URL}/poll/${uuid}`,
          data: {
            questions: this.questions,
            translation: this.currentLocale
          },
          validateStatus: () => true
        }).then((res) => {
          if (res.status === 200) {
            this.uuid = res.data
          }
        })
      } catch {
        this.$axios({
          method: 'POST',
          url: `${process.env.API_URL}/poll`,
          data: {
            questions: this.questions,
            translation: this.currentLocale
          },
          validateStatus: () => true
        }).then((res) => {
          if (res.status !== 200) {
            console.debug(res.data)
          }
        })
      }
    }
  }
}
</script>
