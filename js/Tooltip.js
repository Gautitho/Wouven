class Tooltip
{
  constructor (element, content)
  {
    this.element = element
    this.content = content
    this.tooltip = null
    this.element.addEventListener('mouseover', this.mouseOver.bind(this))
    this.element.addEventListener('mouseout', this.mouseOut.bind(this))
  }

  mouseOver () 
  {
    let tooltip = this.createTooltip()
    let width = tooltip.offsetWidth
    let height = tooltip.offsetHeight
    let left = this.element.offsetWidth / 2 - width / 2 + this.element.getBoundingClientRect().left + document.documentElement.scrollLeft
    let top = 0
    if (this.element.getBoundingClientRect().top - height - 15 + document.documentElement.scrollTop > 10)
    {
      top = this.element.getBoundingClientRect().top - height - 15 + document.documentElement.scrollTop
    }
    else
    {
      top = this.element.getBoundingClientRect().bottom + 15
    }
    tooltip.style.left = left + "px"
    tooltip.style.top = top + "px"
  }

  mouseOut () 
  {
    if (this.tooltip !== null)
    {
      document.body.removeChild(this.tooltip)
      this.tooltip = null
    }
  }

  createTooltip ()
  {
    if (this.tooltip === null) {
      let tooltip = document.createElement('div')
      tooltip.innerHTML = this.content
      tooltip.classList.add('tooltip')
      document.body.appendChild(tooltip)
      this.tooltip = tooltip
    }
    return this.tooltip
  }
}