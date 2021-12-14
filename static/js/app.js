//API requests to the Red List API
document.addEventListener("DOMContentLoaded", function(){
  

let TOKEN = '9bb4facb6d23f48efbf424bb05c0c1ef1cf6f468393bc745d42179ac4aca5fee'
let BASE_URL = 'http://apiv3.iucnredlist.org'





async function getAllSpecies(pageNum) {
    let response = await axios.get(`${BASE_URL}/api/v3/species/page/${pageNum}?token=${TOKEN}`);
    console.log("got", response);

    return response.data.result;
  }




async function getFamiliesAndSpecies(pageNum) {
  let listOfSpecies = await getAllSpecies(pageNum)

    let container = new Object()

    listOfSpecies.forEach(element => {
      const {family_name, scientific_name} = element
      if(container[family_name]){
        container[family_name].push(scientific_name)
      }else{
        container[family_name]=[scientific_name]
      }
    })
    //get rid of plants
    result = _.omit(container, ['FABACEAE', 'MELASTOMATACEAE', 'MYRISTICACEAE'])
   return result
}



//EVENTS
async function loadRedListPage(pageNum) {
    const family_name = document.querySelector('#family_name')
    const speciesUl = document.querySelector('#species')

    let familiesAndSpecies = await getFamiliesAndSpecies(pageNum)

    //put everything on the page
    for (let fam_name of Object.keys(familiesAndSpecies)){

      let newDiv = document.createElement('div')
      
      newDiv.classList.add('dropdown')
      family_name.append(newDiv)
      
      //make the dropdown btn by families
      let newFamilyNameBtn = document.createElement('a')

      newFamilyNameBtn.classList.add('btn', 'btn-success', 'dropdown-toggle')
      newFamilyNameBtn.setAttribute('data-bs-toggle', 'dropdown')
      newFamilyNameBtn.setAttribute('id', fam_name)
      newFamilyNameBtn.setAttribute('role', 'button')
      newFamilyNameBtn.innerText = fam_name
      newDiv.append(newFamilyNameBtn)

      let newUl = document.createElement('ul')
      newUl.classList.add('dropdown-menu')
      newUl.setAttribute('aria-labelledby', fam_name)
      newDiv.append(newUl)

        //display spicies by its families
        for (species_name of familiesAndSpecies[fam_name]){
          let newLi = document.createElement('li')
          let newSpeciesNameLink = document.createElement('a')

          //make the species dropdown items
          newSpeciesNameLink.setAttribute('href', `/animals/${species_name}`) //how to mimic JINJA??
          newSpeciesNameLink.setAttribute('aria-expanded', 'false')
          newSpeciesNameLink.classList.add('list-group-item', 'list-group-item-action', 'dropdown-item')
          newSpeciesNameLink.innerText = species_name
          newLi.append(newSpeciesNameLink)
          newUl.append(newLi)
      }
    }
    
  }


function getPage() {
    let pageForm = document.getElementById('pages')
    console.log(pageForm)
    pageForm.addEventListener('submit', function(e){
      e.preventDefault()
     console.log(e.value)
     console.log('hi')

    })
  }

//Why doesn't it call it?

// {
//   'FABACEAE': ['Fordia incredibilis', 'hi']
// }

loadRedListPage(0)
getPage()

})