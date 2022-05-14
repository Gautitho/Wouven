class Tooltip
{
  constructor (element, content, contentType)
  {
    this.element = element
    this.content = content
    this.contentType = contentType
    this.tooltip = null
    this.mouseOverBind = this.mouseOver.bind(this)
    this.mouseOutBind = this.mouseOut.bind(this)
    this.element.addEventListener('mouseover', this.mouseOverBind)
    this.element.addEventListener('mouseout', this.mouseOutBind)
  }

  destructor ()
  {
    if (document.getElementById("tooltip_" + this.element.id))
    {
      document.body.removeChild(this.tooltip)
    }
    this.element.removeEventListener('mouseover', this.mouseOverBind)
    this.element.removeEventListener('mouseout', this.mouseOutBind)
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
    if (this.tooltip === null) 
    {
      let tooltip = document.createElement('div')
      if (this.contentType == "img")
      {
        tooltip.classList.add('tooltip-img')
        tooltip.style.backgroundImage = "url('" + this.content + "')"
      }
      else if (this.contentType == "txt")
      {
        tooltip.innerHTML = this.content
        tooltip.classList.add('tooltip-txt')
      }
      document.body.appendChild(tooltip)
      tooltip.id    = "tooltip_" + this.element.id
      this.tooltip  = tooltip
    }
    return this.tooltip
  }
}