document.addEventListener("DOMContentLoaded", function() {
  const form = document.querySelector('.autocomplete')   
  const input = document.querySelector('.query input')
  const alert = document.querySelector('.alert')   

  if (alert !== null) {
    window.setTimeout(() => {
      alert.remove()
    }, 2000)
  }
  if (form !== null) {
    form.addEventListener('submit', (event) => {
      event.preventDefault()
    })
  }
  const clearResults = () => {
    const symbols = document.querySelectorAll('.symbol')

    for (const symbol of symbols) {

      symbol.parentNode.removeChild(symbol)
    }
  }

  const search = async (event) => {
    console.log('searching...')
    const token = document.querySelector('[name="csrfmiddlewaretoken"]').value

    clearResults()

    if (event.key === 'Backspace' && input.value.length < 1) {
      clearResults()
    } else if (input.value.length >= 1) {
      let formData = new FormData();
      formData.append("query", input.value)
      formData.append("csrfmiddlewaretoken", token)

      // if filter (search by name)
      // param = '&include_name_in_search='true'
      await axios.get(`/search?query=${input.value}`)
      .then(({ data: { data }}) => {
        for (const ticker of data) {
          const el = document.createElement('div')
          const symbol = ticker.split('-')[0].replace(' ', '')

          el.classList.add('symbol')
          el.innerText = ticker
          el.setAttribute('data-value', symbol)
          el.addEventListener('click', liveUpdate)

          form.after(el)
        }
      })
      .catch(err => console.log(err))
    }
  }

  const liveUpdate = async (event) => {
    const symbol = event.currentTarget.getAttribute('data-value')
    const el = document.createElement('div')

    clearResults()

    // Create loader
    el.innerHTML = 'Loading...'
    el.classList.add('loader')
    form.after(el)

    // Protected route (Must be superuser)
      return await axios.get(`/search/live_update/?symbol=${symbol}`)
      .then(({data}) => {
        print(data)
        const el = document.createElement('div')
        const previousElement = document.querySelector('.current-price')
        const loader = document.querySelector('.loader')

        // Clear loader
        loader.parentElement.removeChild(loader)

        // Remove last price
        if (previousElement !== null) {
          previousElement.parentNode.removeChild(previousElement)
        }


        if (data.error) {
          console.log('Please sign in as superuser')
          const error = document.createElement('a')
          error.innerText = 'Please sign in. Only the admin can use this site currently.'
          form.after(error)
          return
        }
        // const formattedPrice = data.regularMarketPrice.fmt

        const priceText = 'Current price quote: $' + data.price

        el.innerText = priceText
        el.classList.add('current-price')

        // Create URL
        const watchButton = document.createElement('a')
        watchButton.innerText = 'Watch This Stock?'
        watchButton.href = `search/watch/${symbol}/?price=${data.price}`

        form.after(el)
        el.after(watchButton)
      })
      .catch(err => {
        console.log(err)
      })
  }

  if (input !== null) {

    input.addEventListener('input', search)
  }


  window.onunload = function() {
    input.removeEventListener('input', search)
    form.removeEventListener('submit', (event) => {
      event.preventDefault()
    })
  }
});
