import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import ChatMarkdown from './ChatMarkdown'

describe('ChatMarkdown', () => {
  it('renders bold syntax as a bold element instead of literal asterisks', () => {
    render(<ChatMarkdown content="Studying **Financial Management** is useful." />)
    const bold = screen.getByText('Financial Management')
    expect(bold.tagName.toLowerCase()).toBe('strong')
    expect(screen.queryByText(/\*\*/)).not.toBeInTheDocument()
  })

  it('renders a level-3 heading as a heading element instead of literal hashes', () => {
    render(<ChatMarkdown content={'### Course Overview Roadmap'} />)
    const heading = screen.getByText('Course Overview Roadmap')
    expect(heading.tagName.toLowerCase()).toBe('h3')
    expect(screen.queryByText(/###/)).not.toBeInTheDocument()
  })

  it('renders an ordered list as list items', () => {
    render(<ChatMarkdown content={'1. First step\n2. Second step'} />)
    expect(screen.getByText('First step').tagName.toLowerCase()).toBe('li')
    expect(screen.getByText('Second step').tagName.toLowerCase()).toBe('li')
  })

  it('renders italic syntax as an emphasis element', () => {
    render(<ChatMarkdown content="*Why?* Because reasons." />)
    expect(screen.getByText('Why?').tagName.toLowerCase()).toBe('em')
  })

  it('renders a horizontal rule as a divider rather than literal dashes', () => {
    const { container } = render(<ChatMarkdown content={'First section\n\n---\n\nSecond section'} />)
    expect(container.querySelector('hr')).toBeInTheDocument()
  })
})