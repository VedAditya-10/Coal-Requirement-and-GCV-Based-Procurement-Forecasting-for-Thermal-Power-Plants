fetch('/plants')
    .then(r => r.json())
    .then(plants => {
        const select = document.getElementById('plant');
        plants.forEach(p => {
            const option = document.createElement('option');
            option.value = p;
            option.textContent = p;
            select.appendChild(option);
        });
    });

const typeBtns = document.querySelectorAll('.type-btn');
const existingInputs = document.getElementById('existingPlantInputs');
const newInputs = document.getElementById('newPlantInputs');
let isNewPlant = false;

typeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        typeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        const type = btn.dataset.type;
        isNewPlant = (type === 'new');
        
        if (isNewPlant) {
            existingInputs.style.display = 'none';
            newInputs.style.display = 'block';
            document.getElementById('plant').removeAttribute('required');
            document.getElementById('capacity').setAttribute('required', '');
        } else {
            existingInputs.style.display = 'block';
            newInputs.style.display = 'none';
            document.getElementById('plant').setAttribute('required', '');
            document.getElementById('capacity').removeAttribute('required');
        }
    });
});

document.getElementById('forecastForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    
    loading.classList.add('show');
    result.classList.remove('show');
    
    const data = {
        year: parseInt(document.getElementById('year').value),
        month: parseInt(document.getElementById('month').value),
        is_new_plant: isNewPlant
    };
    
    if (isNewPlant) {
        data.capacity = parseFloat(document.getElementById('capacity').value);
        data.technology = document.getElementById('technology').value;
    } else {
        data.plant_key = document.getElementById('plant').value;
    }
    
    try {
        const response = await fetch('/forecast', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        const forecast = await response.json();
        
        if (forecast.error) {
            alert('Error: ' + forecast.error);
            loading.classList.remove('show');
            return;
        }
        
        document.getElementById('resultPlant').textContent = forecast.plant_name || 'New Plant';
        document.getElementById('resultPLF').textContent = forecast.plf_percentage.toFixed(2) + '%';
        document.getElementById('resultElectricity').textContent = forecast.electricity_mwh.toLocaleString() + ' MWh';
        document.getElementById('resultCoal').textContent = forecast.coal_required_tonnes.toLocaleString() + ' tonnes';
        document.getElementById('resultGrade').textContent = forecast.coal_grade;
        
        loading.classList.remove('show');
        result.classList.add('show');
    } catch (error) {
        alert('Error: ' + error.message);
        loading.classList.remove('show');
    }
});
