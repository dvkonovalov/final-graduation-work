const charts = {};
let coin_map = {
    bitcoin: "btc",
    ethereum: "eth",
    litecoin: "ltc"
};

function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));
    document.getElementById(tabId).classList.remove('hidden');

    document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('bg-blue-500', 'text-white');
    btn.classList.add('bg-gray-300', 'text-gray-800');
    });

    const index = ['btc', 'eth', 'ltc'].indexOf(tabId);
    document.querySelectorAll('.tab-btn')[index].classList.add('bg-blue-500', 'text-white');
}

function resetZoom(chartId) {
      if (charts[chartId]) charts[chartId].resetZoom();
    }

function createChart(id, label, labels, data) {
    const ctx = document.getElementById(id).getContext('2d');
    if (charts[id]) charts[id].destroy();
    charts[id] = new Chart(ctx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
        label: label,
        data: data,
        borderColor: 'rgba(59,130,246,1)',
        backgroundColor: 'rgba(59,130,246,0.1)',
        fill: true,
        tension: 0.4
        }]
    },
    options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            zoom: {
              pan: {
                enabled: true,
                mode: 'xy',
              },
              zoom: {
                wheel: {
                  enabled: true,
                },
                pinch: {
                  enabled: true,
                },
                drag: {
                  enabled: true,
                  backgroundColor: 'rgba(0,0,0,0.1)',
                  borderColor: 'rgba(0,0,0,0.3)',
                  borderWidth: 1,
                },
                mode: 'xy',
              },
              limits: {
                y: { min: 'original', max: 'original' },
                x: { min: 'original', max: 'original' }
              }
            }
          },
          scales: {
            y: { beginAtZero: false }
          },
          onClick: (e, elements, chart) => {
            if (e.detail === 2) {
              chart.resetZoom();
            }
          }
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const init = {
        btc: [],
        eth: [],
        ltc: []
    };
    const labels = {
        btc: [],
        eth: [],
        ltc: []
    };

    var last_btc;
    var last_eth;
    var last_lit;

    axios.get('/get_all_data')
            .then(function (response) {
                const currencies = response.data;
                currencies.forEach(currency => {
                    if (currency.name == 'bitcoin'){
                        last_btc = currency;
                    }
                    else if (currency.name == 'ethereum'){
                        last_eth = currency;
                    }
                    else{
                        last_lit = currency;
                    }
                    init[coin_map[currency.name.toLowerCase()]].push(currency.price);
                    labels[coin_map[currency.name.toLowerCase()]].push(currency.created_date);
                });
                const tableBody = document.getElementById(`btc-table`).querySelector('tbody');
                tableBody.innerHTML = '';
                [last_btc, last_eth, last_lit].forEach(currency => {
                    const row = tableBody.insertRow();
                    const cell1 = row.insertCell(0);
                    const cell2 = row.insertCell(1);
                    const cell3 = row.insertCell(2);

                    cell1.textContent = currency.name;
                    cell2.textContent = '$' + currency.price.toFixed(2);
                    cell3.innerHTML = currency.change > 0
                        ? `<span class="text-green-600">+${currency.change}</span>`
                        : `<span class="text-red-600">${currency.change}</span>`;
                });
            })
            .catch(function (error) {
                console.error(error);
                alert('Ошибка при получении данных. Проверьте сервер.');
            });
    ['btc', 'eth', 'ltc'].forEach(coin => {
        createChart(`${coin}Chart`, `${coin.toUpperCase()} Forecast`, labels[coin], init[coin]);
    });

    document.querySelectorAll('.update-button').forEach(button => {
        button.addEventListener('click', function () {
            const coin = this.dataset.coin;
            const chart = charts[`${coin}Chart`];
            const lastLabel = chart.data.labels.at(-1);

            axios.get('/update', { params: { created_date: lastLabel } })
            .then(function (response) {
                const currencies = response.data;
                const tableBody = document.getElementById(`${coin}-table`).querySelector('tbody');
                if (currencies.length != 0){
                    tableBody.innerHTML = '';
                }

                currencies.forEach(currency => {
                    const row = tableBody.insertRow();
                    const cell1 = row.insertCell(0);
                    const cell2 = row.insertCell(1);
                    const cell3 = row.insertCell(2);

                    cell1.textContent = currency.name;
                    cell2.textContent = '$' + currency.price.toFixed(2);
                    cell3.innerHTML = currency.change > 0
                        ? `<span class="text-green-600">+${currency.change}%</span>`
                        : `<span class="text-red-600">${currency.change}%</span>`;
                    

                    const currentChart = charts[`${coin_map[currency.name.toLowerCase()]}Chart`]; 
                    currentChart.data.labels.push(currency.created_date);
                    currentChart.data.datasets[0].data.push(currency.price);
                    currentChart.update();
                });
            })
            .catch(function (error) {
                console.error(error);
                alert('Ошибка при получении данных. Проверьте сервер.');
            });
    });
    });
});