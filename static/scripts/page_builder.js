request = function(url) {
    console.log(url)
    return fetch(url,options={'method':'post'})
}

fetch( 'http://10.0.0.177:5000/check_devices')
    .then( response => response.json() )
    .then( devices => {
        console.log(devices)
        for (var deviceType in devices) {
            parent = document.createElement('div')
            document.body.appendChild(parent)
            console.log(deviceType)
            for (var deviceAliasKey in devices[deviceType]) {
                let deviceAlias = devices[deviceType][deviceAliasKey]
                let btnOn = document.createElement('button')
                let btnOff = document.createElement('button')
                btnOn.innerHTML = 'Turn on ' + deviceAlias
                btnOff.innerHTML = 'Turn off ' + deviceAlias
                btnOn.value = 'http://10.0.0.177:5000/device_action/' + deviceAlias + '/power/1'
                btnOff.value = 'http://10.0.0.177:5000/device_action/' + deviceAlias + '/power/0' 
                btnOn.addEventListener('click',function() {request(btnOn.value)})
                btnOff.addEventListener('click',function() {request(btnOff.value)})
                parent.appendChild(btnOn)
                parent.appendChild(btnOff)
                }
            document.body.appendChild(document.createElement('br'))
            }
        }
    )
