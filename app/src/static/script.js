document.addEventListener('DOMContentLoaded', function() {
    console.log('Script loaded');

    var ctx = document.getElementById('chart').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Bitcoin Price',
                data: [10000, 12000, 11000, 13000, 14000, 15000, 16000, 17000, 18000, 19000, 20000, 21000],
                backgroundColor: 'rgba(75,192,192,0.4)',
                borderColor: 'rgba(75,192,192,1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                },
                x: {
                    type: 'category',
                    display: true,
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxTicksLimit: 10
                    }
                }
            },
            pan: {
                enabled: true,
                mode: 'xy'
            },
            zoom: {
                enabled: true,
                mode: 'x'
            }
        }
    });

    document.getElementById('update-button').addEventListener('click', function() {
        var last_elem = chart.data.labels.at(-1);
        console.log(last_elem);
        axios.get('/update', {params:{created_date:last_elem}})
            .then(function(response) {
                var currencies = response.data;
                var tableBody = document.getElementById('currency-table');
                tableBody.innerHTML = '';
                currencies.forEach(function(currency) {
                    var row = tableBody.insertRow();
                    var cell1 = row.insertCell(0);
                    var cell2 = row.insertCell(1);
                    var cell3 = row.insertCell(2);
                    cell1.innerHTML = currency.name;
                    cell2.innerHTML = '$' + currency.price;
                    cell3.innerHTML = currency.change > 0 ? '<span style="color: green;">+' + currency.change + '%</span>' : '<span style="color: red;">' + currency.change + '%</span>';
                    if (currency.name == "Bitcoin"){
                        chart.data.datasets[0].data.push(currency.price);
                        console.log(currency.created_date);
                        console.log(currency);
                        chart.data.labels.push(currency.created_date);
                        chart.update();
                    }
                });
            })
            .catch(function(error) {
                console.error(error);
            });
    });
});