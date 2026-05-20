import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PlayerSearch } from '@/components/player/PlayerSearch'

describe('PlayerSearch', () => {
  const mockOnChange = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders search input with correct placeholder', () => {
    render(<PlayerSearch value="" onChange={mockOnChange} />)
    
    const input = screen.getByPlaceholderText('Search players or teams...')
    expect(input).toBeInTheDocument()
    expect(input).toHaveValue('')
  })

  it('displays current value', () => {
    render(<PlayerSearch value="test query" onChange={mockOnChange} />)
    
    const input = screen.getByPlaceholderText('Search players or teams...')
    expect(input).toHaveValue('test query')
  })

  it('calls onChange when user types', async () => {
    const user = userEvent.setup()
    render(<PlayerSearch value="" onChange={mockOnChange} />)
    
    const input = screen.getByPlaceholderText('Search players or teams...')
    await user.type(input, 'test')
    
    // Should debounce, so onChange might not be called immediately
    // Wait for debounce timeout
    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalledWith('test')
    }, { timeout: 400 })
  })

  it('is disabled when disabled prop is true', () => {
    render(<PlayerSearch value="" onChange={mockOnChange} disabled={true} />)
    
    const input = screen.getByPlaceholderText('Search players or teams...')
    expect(input).toBeDisabled()
  })

  it('uses custom placeholder', () => {
    render(
      <PlayerSearch 
        value="" 
        onChange={mockOnChange} 
        placeholder="Custom placeholder" 
      />
    )
    
    const input = screen.getByPlaceholderText('Custom placeholder')
    expect(input).toBeInTheDocument()
  })
})
