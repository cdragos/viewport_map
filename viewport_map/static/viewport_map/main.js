'use strict';

class GoogleMaps extends React.Component {

  static validAddressTypes = [
    'route', 'street_address', 'intersection', 'point_of_interest', 'park']
  static mapLayer = null

  constructor(props) {
    super(props)
    this.handleMapClick = this.handleMapClick.bind(this)
    this.map = null;
  }

  drawFusionTableLayer() {
    const table_id = document.getElementById('table-id').value
    const layer = new google.maps.FusionTablesLayer({
      query: {
        select: '\'Location\'',
        from: table_id,
        where: 'location not equal to' + (Math.floor(Math.random() * 10000000)).toString()
      }
    })
    layer.setMap(this.map)
    GoogleMaps.mapLayer = layer
  }

  componentDidMount() {
    this.map = new google.maps.Map(document.getElementById('map'), {
      center: {lat: -34.397, lng: 150.644},
      zoom: 10
    })
    this.map.addListener('click', this.handleMapClick)
    this.drawFusionTableLayer()
  }

  handleMapClick(location) {
    const geocoder = new google.maps.Geocoder()

    geocoder.geocode({location: location.latLng}, (results, status) => {
      if (status !== 'OK') return

      const {types, formatted_address} = results[0]
      const isValidAddress = types.filter(
          value => -1 !== GoogleMaps.validAddressTypes.indexOf(value)).length > 0;

      if(isValidAddress) {
        this.props.handleLocationChange(
          location.latLng, formatted_address,
          this.drawFusionTableLayer.bind(this));
      }
    });
  }

  render() {
    return <div id="map" className="map-container"></div>
  }

}


class Locations extends React.Component {

  async componentDidMount() {
    let response = await fetch('api/locations', {credentials: 'same-origin'})
    let data = await response.json()
    this.props.handleLoadingLocations(data.locations)
  }

  render() {
    return (
      <div id="locations" className="locations-container">
        <div className="clear-locations">
          <a href="" onClick={this.props.handleClearLocations}>Clear Locations</a>
          </div>
        <ul>
          {this.props.locations.map((item, index) => (
            <li key={index}>{item.address}</li>
          ))}
        </ul>
      </div>
    );
  }

}


class ViewPort extends React.Component {

  constructor(props) {
    super(props)
    this.state = {'locations': [], 'locations_cleared': false}
    this.handleLoadingLocations = this.handleLoadingLocations.bind(this)
    this.handleLocationChange = this.handleLocationChange.bind(this)
    this.handleClearLocations = this.handleClearLocations.bind(this)
  }

  async handleLoadingLocations(locations) {
    this.setState({ locations: locations })
  }

  async handleLocationChange(latLng, address, drawFusionTableLayer) {
    const formData = {latitude: latLng.lat(), longitude: latLng.lng(), address: address}
    let response = await fetch('api/locations', {
      method: 'POST',
      body: JSON.stringify(formData),
      credentials: 'same-origin'
    })
    let data = await response.json()
    drawFusionTableLayer()
    this.setState(prevState => ({ locations: prevState.locations.concat([data.location]) }))
  }

  async handleClearLocations(e) {
    e.preventDefault()
    let response = await fetch('api/clear_locations', {
      method: 'DELETE',
      credentials: 'same-origin'
    })
    GoogleMaps.mapLayer.setMap(null)
    this.setState({locations: []})
  }

  render() {
    return (
      <div className="viewport-container">
        <GoogleMaps handleLocationChange={this.handleLocationChange} />
        <Locations locations={this.state.locations}
                   handleClearLocations={this.handleClearLocations}
                   handleLoadingLocations={this.handleLoadingLocations} />
      </div>
    )
  }

}

const viewport_container = document.querySelector('#viewport_container')
ReactDOM.render(<ViewPort />, viewport_container)
