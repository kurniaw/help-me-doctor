// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',

  modules: [
    '@pinia/nuxt',
    '@primevue/nuxt-module',
    '@nuxt/eslint',
  ],

  typescript: {
    strict: true,
    typeCheck: true,
  },

  primevue: {
    options: {
      theme: {
        preset: 'Aura',
        options: {
          darkModeSelector: '.dark-mode',
          cssLayer: false,
        },
      },
      ripple: true,
    },
    components: {
      include: [
        'Button',
        'InputText',
        'Password',
        'Card',
        'Toast',
        'Message',
        'Badge',
        'ProgressSpinner',
        'Textarea',
        'Divider',
        'Avatar',
      ],
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    },
  },

  css: ['primeicons/primeicons.css', '~/assets/css/main.css'],

  app: {
    head: {
      title: 'HelpMeDoctor — Singapore Medical Triage',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI-powered Singapore medical and legal triage assistant' },
      ],
    },
  },

  eslint: {
    config: {
      stylistic: false,
    },
  },
})
