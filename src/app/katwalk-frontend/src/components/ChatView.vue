<template>
  <div class="container">
    <input 
      v-on:keyup.enter="send" 
      v-model="prompt" 
      class="form-control form-control-lg" 
      type="text" 
      placeholder="Write a prompt and hit enter" 
      aria-label=".form-control-lg example"
      :disabled="disabled"
    />
  </div>
  <div class="container">
    <div class="row">
      <div class="col-12">
        <div class="response">
          {{ response }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
    data() {
      return {
        disabled: false,
        prompt: "",
        response: ""
      }
    },
    methods: {
      send: async function () {
        const _prompt = this.prompt
        this.disabled = true
        
        try {
          const dataToSend = { "prompt": _prompt };
          const apiUrl = process.env.VUE_APP_BACKEND_DNS
          
          console.log(`API URL - ${apiUrl}`)

          const response = await fetch(apiUrl, {
            method: 'POST',
            mode: 'cors',
            headers: {
              'Content-Type': 'application/json',
              'accept': 'application/json'
            },
            body: JSON.stringify(dataToSend)
          });

          if (!response.ok) 
          {
            throw new Error('Network response was not ok');
          }
          
          const responseData = await response.json();
          this.response = responseData.text[0];
          this.disabled = false
          this.prompt = ""

        } 
        catch (error) 
        {
          this.disabled = false
          this.response = 'Sorry, we cannot generate a response at this time'
          console.error('Error sending POST request:', error);
        }

      }
    }
  }
</script>
<style>
.response{
  border: 1px solid #FFA3FD;
  padding: 10px;
  border-radius: 10px;
  margin-top: 30px;
  height: calc(100vh - 180px);
  overflow-y: scroll;
  overflow-x: hidden;
  font-size: 20px;
  text-align: justify;
  color: #FFA3FD;
}

input[type="text"], input[type="text"]:focus{
  background: transparent;
  border-color: #FFA3FD;
  color: #FFA3FD;
  outline: none !important;
}

input[type="text"]:disabled{
  background-color:#25252b;
}

::placeholder { /* Chrome, Firefox, Opera, Safari 10.1+ */
  color: #FFA3FD !important;
  opacity: 1; /* Firefox */
}

:-ms-input-placeholder { /* Internet Explorer 10-11 */
  color: #FFA3FD;
}

::-ms-input-placeholder { /* Microsoft Edge */
  color: #FFA3FD;
}
</style>
