import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import MessageBubble from '~/components/chat/MessageBubble.vue'
import type { Message } from '~/types/chat'

const makeMessage = (overrides: Partial<Message> = {}): Message => ({
  id: 'test-1',
  role: 'assistant',
  content: 'Hello, this is a test message.',
  timestamp: new Date('2024-01-01T10:00:00'),
  ...overrides,
})

describe('MessageBubble', () => {
  it('renders assistant message', () => {
    const wrapper = mount(MessageBubble, {
      props: { message: makeMessage() },
    })
    expect(wrapper.find('.bubble-assistant').exists()).toBe(true)
    expect(wrapper.text()).toContain('Hello, this is a test message.')
  })

  it('renders user message on the right', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: makeMessage({ role: 'user', content: 'I have chest pain' }),
      },
    })
    expect(wrapper.find('.bubble-user').exists()).toBe(true)
    expect(wrapper.find('.is-user').exists()).toBe(true)
    expect(wrapper.text()).toContain('I have chest pain')
  })

  it('shows urgency badge for CRITICAL', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: makeMessage({ urgency: 'CRITICAL' }),
      },
    })
    expect(wrapper.text()).toContain('CRITICAL')
  })

  it('shows urgency badge for HIGH', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: makeMessage({ urgency: 'HIGH' }),
      },
    })
    expect(wrapper.text()).toContain('HIGH')
  })

  it('does not show urgency badge for user messages', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: makeMessage({ role: 'user', urgency: 'CRITICAL' }),
      },
    })
    expect(wrapper.find('.badge-row').exists()).toBe(false)
  })

  it('strips URGENCY: prefix from content', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: makeMessage({ content: 'URGENCY:CRITICAL\n\nActual response content here.' }),
      },
    })
    const html = wrapper.find('.bubble-assistant').html()
    expect(html).not.toContain('URGENCY:CRITICAL')
    expect(html).toContain('Actual response content here.')
  })

  it('shows pathway label when provided', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: makeMessage({ urgency: 'HIGH', pathway: 'MEDICAL' }),
      },
    })
    expect(wrapper.text()).toContain('MEDICAL')
  })

  it('applies CRITICAL urgency border class', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: makeMessage({ urgency: 'CRITICAL' }),
      },
    })
    expect(wrapper.find('.bubble-critical').exists()).toBe(true)
  })

  it('shows LOW urgency badge without alert banner', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: makeMessage({ urgency: 'LOW' }),
      },
    })
    expect(wrapper.text()).toContain('LOW')
    expect(wrapper.find('.urgency-alert').exists()).toBe(false)
    expect(wrapper.find('.bubble-low').exists()).toBe(true)
  })
})
