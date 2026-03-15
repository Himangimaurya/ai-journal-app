import { useState } from "react"
import axios from "axios"

function App() {

const [text,setText] = useState("")
const [emotion,setEmotion] = useState("")
const [insight,setInsight] = useState({})

const userId = "user1"

const saveJournal = async () => {

const res = await axios.post(
"http://127.0.0.1:8000/api/journal",
{
userId:userId,
ambience:"forest",
text:text
})

setEmotion(res.data.emotion)
}

const getInsights = async () => {

const res = await axios.get(
`http://127.0.0.1:8000/api/journal/insights/${userId}`
)

setInsight(res.data)

}

return (
<div style={{padding:"40px",fontFamily:"Arial"}}>

<h2>AI Journal</h2>

<textarea
rows="6"
cols="50"
placeholder="Write your journal..."
onChange={(e)=>setText(e.target.value)}
/>

<br/><br/>

<button onClick={saveJournal}>Save Journal</button>

<button onClick={getInsights}>Get Insights</button>

<h3>Emotion</h3>
<p>{emotion}</p>

<h3>Insights</h3>
<pre>{JSON.stringify(insight,null,2)}</pre>

</div>
)
}

export default App