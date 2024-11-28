document.addEventListener('DOMContentLoaded', () => {
    const map = L.map('map').setView([19.0760, 72.8777], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);

    const countrySelect = document.getElementById('country-select');
    const stateSelect = document.getElementById('state-select');
    const citySelect = document.getElementById('city-select');
    const projectSelect = document.getElementById('project-select');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const submitBtn = document.getElementById('submitBtn');

    // Populate dropdowns
    data.countries.forEach(country => {
        let option = document.createElement('option');
        option.value = country;
        option.textContent = country;
        countrySelect.appendChild(option);
    });

    data.states.forEach(state => {
        let option = document.createElement('option');
        option.value = state;
        option.textContent = state;
        stateSelect.appendChild(option);
    });

    data.cities.forEach(city => {
        let option = document.createElement('option');
        option.value = city;
        option.textContent = city;
        citySelect.appendChild(option);
    });

    data.projects.forEach(project => {
        let option = document.createElement('option');
        option.value = project;
        option.textContent = project;
        projectSelect.appendChild(option);
    });

    uploadBtn.addEventListener('click', () => {
        const file = fileInput.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert('File uploaded successfully');
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        } else {
            alert('Please select a file to upload');
        }
    });

    submitBtn.addEventListener('click', () => {
        const country = countrySelect.value;
        const state = stateSelect.value;
        const city = citySelect.value;
        const project = projectSelect.value;

        fetch(`/get_data?country=${country}&state=${state}&city=${city}&project=${project}`)
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                // Update the map based on the project data
                map.setView(data.coords, 13);
                fetch('/orthomosaic')
                    .then(response => response.blob())
                    .then(imageBlob => {
                        const url = URL.createObjectURL(imageBlob);
                        const orthomosaicLayer = L.imageOverlay(url, map.getBounds());
                        orthomosaicLayer.addTo(map);
                    });
            })
            .catch(error => console.error('Error:', error));
    });
});
