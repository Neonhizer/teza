document.addEventListener('DOMContentLoaded', function() {
    var map;
    // Inițializați harta și alți handlere necesare aici
    
    // Adăugați event listener pe categorii
    document.querySelectorAll('ul li a').forEach(function(categoryLink) {
      categoryLink.addEventListener('click', function(e) {
        e.preventDefault();
        var category = this.textContent.trim().toLowerCase(); // În funcție de cum aveți setate categoriile, această linie poate necesita ajustări
        showCategory(category);
      });
    });
    
    function showCategory(category) {
      fetch('/get_events_by_category/' + category)
        .then(response => response.json())
        .then(data => {
          displayEvents(data.events);
          document.getElementById('events-modal').style.display = 'block'; // Afișați modalul
        })
        .catch(error => console.error('Error:', error));
    }
    
    function displayEvents(events) {
      var eventsContent = document.getElementById('events-content');
      eventsContent.innerHTML = ''; // Goliți conținutul curent
    
      events.forEach(function(event) {
        var eventElement = document.createElement('div');
        eventElement.innerHTML = '<h3>' + event.title + '</h3>' +
                                 '<p>' + event.description + '</p>';
        eventsContent.appendChild(eventElement);
      });
    }
    
    function closeEventsModal() {
      document.getElementById('events-modal').style.display = 'none'; // Ascundeți modalul
    }
  });
  
  