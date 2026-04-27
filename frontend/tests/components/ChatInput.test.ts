import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ChatInput from '~/components/chat/ChatInput.vue'

describe('ChatInput', () => {
  it('emits send event when button clicked', async () => {
    const wrapper = mount(ChatInput, {
      props: { streaming: false },
    })
    await wrapper.find('.chat-textarea').setValue('I have chest pain')
    await wrapper.find('.send-btn').trigger('click')
    expect(wrapper.emitted('send')).toBeTruthy()
    expect(wrapper.emitted('send')?.[0]).toEqual(['I have chest pain'])
  })

  it('clears input after sending', async () => {
    const wrapper = mount(ChatInput, {
      props: { streaming: false },
    })
    const textarea = wrapper.find('.chat-textarea')
    await textarea.setValue('test message')
    await wrapper.find('.send-btn').trigger('click')
    expect((textarea.element as HTMLTextAreaElement).value).toBe('')
  })

  it('does not emit when input is empty', async () => {
    const wrapper = mount(ChatInput, {
      props: { streaming: false },
    })
    await wrapper.find('.send-btn').trigger('click')
    expect(wrapper.emitted('send')).toBeFalsy()
  })

  it('disables input when streaming', () => {
    const wrapper = mount(ChatInput, {
      props: { streaming: true },
    })
    const textarea = wrapper.find('.chat-textarea')
    expect((textarea.element as HTMLTextAreaElement).disabled).toBe(true)
  })

  it('disables send button when streaming', () => {
    const wrapper = mount(ChatInput, {
      props: { streaming: true },
    })
    const btn = wrapper.find('.send-btn')
    expect((btn.element as HTMLButtonElement).disabled).toBe(true)
  })

  it('emits send on Enter key (without shift)', async () => {
    const wrapper = mount(ChatInput, {
      props: { streaming: false },
    })
    await wrapper.find('.chat-textarea').setValue('Enter key test')
    await wrapper.find('.chat-textarea').trigger('keydown.enter')
    expect(wrapper.emitted('send')).toBeTruthy()
  })

  it('does not emit when only whitespace', async () => {
    const wrapper = mount(ChatInput, {
      props: { streaming: false },
    })
    await wrapper.find('.chat-textarea').setValue('   ')
    await wrapper.find('.send-btn').trigger('click')
    expect(wrapper.emitted('send')).toBeFalsy()
  })
})
