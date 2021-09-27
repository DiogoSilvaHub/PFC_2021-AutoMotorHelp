


firebase.auth().onAuthStateChanged((user) => {
  if (user) {
		document.getElementById("loggedin").style.display="block";
		document.getElementById("notlogged").style.display="none";
		const user=firebase.auth().currentUser;
		document.getElementById("user").innerHTML = "Welcome "+user.email.split("@")[0];
 
  } else {
		document.getElementById("loggedin").style.display="none";
		document.getElementById("notlogged").style.display="block";
		if(location.href.split("/").pop()!="index.html")		
			location.href = "index.html";
  }
});

function numberValues(timeUn,dateAt,cb){
	const values=[]
	timeUn=timeUn.toLowerCase()
	let getTime="getFullYear"
	let test=()=>true
	let nextTimeUn="months"
	switch (timeUn){
		case "months":
			getTime="getMonth"
			test=(date)=>date.getFullYear()==dateAt[0]
			nextTimeUn="days"
			break
		case "days":
			getTime="getDate"
			test=(date)=>date.getFullYear()==dateAt[0] && date.getMonth()==dateAt[1]-1
			nextTimeUn="hours"
			break
		case "hours":
			getTime="getHours"
			test=(date)=>date.getFullYear()==dateAt[0] && date.getMonth()==dateAt[1]-1 && date.getDate()==dateAt[2]
			nextTimeUn="minutes"
			break
		case "minutes":
			getTime="getMinutes"
			test=(date)=>date.getFullYear()==dateAt[0] && date.getMonth()==dateAt[1]-1 && date.getDate()==dateAt[2] && date.getHours()==dateAt[3]
			nextTimeUn="seconds"
			break
		case "seconds":
			getTime="getSeconds"
			test=(date)=>date.getFullYear()==dateAt[0] && date.getMonth()==dateAt[1]-1 && date.getDate()==dateAt[2] && date.getHours()==dateAt[3] && date.getMinutes()==dateAt[4]
			break
		default:
			timeUn="years"
	}
	let data=false
	firebase.auth().onAuthStateChanged((user) => {
		storage.ref(user.uid).listAll().then((res)=>res.items.forEach(i=>{
			data=true
			const path=i.toString().split("/")
			const pathDate=path[path.length-1].split(".wav")[0]
			const date=new Date(Date.parse(pathDate))
			if(test(date)){
				values.push(date[getTime]())
			}
			})).then(()=>{
				if(!values.length){
					if(data){
						alert("Change date or narrow the date scope")
						return cb({chart:{0:0},nexTimeUnit:nextTimeUn,timeUnit:timeUn})
					}
					alert("No anamolies detected")
					return cb({chart:{0:timeUn},nexTimeUnit:nextTimeUn,timeUnit:timeUn})
				}
				values.sort((a,b)=>a-b)
				const counts={}
				let prevNum=null
				for(i in values){
					let num=values[i]
					if(timeUn=="months")
						num++
					if(num!=undefined)
						counts[num]=counts[num] ? counts[num] +1 : 1
					if(prevNum && num-prevNum>1)
						for(let i=prevNum+1;i<num;i++)
							counts[i]=0
					prevNum=num
				}
				cb({chart:counts,nextTimeUnit:nextTimeUn,timeUnit:timeUn})
			}).catch((err)=>window.alert(err.message))
	})
}
function durationValues(timeUn,dateAt,cb){
	const values=[]
	timeUn=timeUn.toLowerCase()
	let getTime="getFullYear"
	let test=()=>true
	let nextTimeUn="months"
	switch (timeUn){
		case "months":
			getTime="getMonth"
			test=(date)=>date.getFullYear()==dateAt[0]
			nextTimeUn="days"
			break
		case "days":
			getTime="getDate"
			test=(date)=>date.getFullYear()==dateAt[0] && date.getMonth()==dateAt[1]-1
			nextTimeUn="hours"
			break
		case "hours":
			getTime="getHours"
			test=(date)=>date.getFullYear()==dateAt[0] && date.getMonth()==dateAt[1]-1 && date.getDate()==dateAt[2]
			nextTimeUn="minutes"
			break
		case "minutes":
			getTime="getMinutes"
			test=(date)=>date.getFullYear()==dateAt[0] && date.getMonth()==dateAt[1]-1 && date.getDate()==dateAt[2] && date.getHours()==dateAt[3]
			nextTimeUn="seconds"
			break
		case "seconds":
			getTime="getSeconds"
			test=(date)=>date.getFullYear()==dateAt[0] && date.getMonth()==dateAt[1]-1 && date.getDate()==dateAt[2] && date.getHours()==dateAt[3] && date.getMinutes()==dateAt[4]
			break
		default:
			timeUn="years"
	}
	let data=false
	const durations=[]
	const proms=[]
	firebase.auth().onAuthStateChanged((user) => {
		storage.ref(user.uid).listAll().then((res)=>res.items.forEach(i=>{
			data=true
			const path=i.toString().split("/")
			const pathDate=path[path.length-1].split(".wav")[0]
			const date=new Date(Date.parse(pathDate))
			if(test(date)){
				proms.push(i.getMetadata().then(metada=>{
					const dur= Math.round(metada.size*8/16/22050*10)/10 //duration=size*8/bitsPerSample/samplesPerSecond/channels
					values.push({"date":date[getTime](),"duration":dur})
				}).catch(err=>alert(err)))
			}
			})).then(()=>{
					Promise.all(proms).then(()=>{
						if(!values.length){
						if(data){
							alert("Change date or narrow the date scope")
							return cb({chart:{0:0},nexTimeUnit:nextTimeUn,timeUnit:timeUn})
						}
						alert("No anamolies detected")
						return cb({chart:{0:timeUn},nexTimeUnit:nextTimeUn,timeUnit:timeUn})
					}
					values.sort((a,b)=>a.date-b.date)
					const secs={}
					let prevNum=null
					for(let i in values){
						let num=values[i].date
						if(timeUn=="months")
							num++
						if(num!=undefined)
							secs[num]=secs[num] ? secs[num] +values[i].duration : values[i].duration
						if(prevNum && num-prevNum>1)
							for(let i=prevNum+1;i<num;i++)
								secs[i]=0
						prevNum=num
					}
					cb({chart:secs,nextTimeUnit:nextTimeUn,timeUnit:timeUn})
				})
			}).catch((err)=>window.alert(err.message))
	})
}
function playAudioFrom(date){
	firebase.auth().onAuthStateChanged((user) => {
		storage.ref(user.uid).listAll().then( (res)=>{
			res.items.forEach(i=>{
				const path=i.toString().split("/")
				const file=path[path.length-1]
				if(file.startsWith(date)){
					storage.ref(user.uid).child(file).getDownloadURL().then(function(url) {
					const audio = document.getElementById('myAudio');
					audio.src = url;
					audio.play()
					})
				}	
			})
		});
	})
}
function buttons(){
	const dates=[]
	const im=document.getElementById("image")
	firebase.auth().onAuthStateChanged((user) => {
		storage.ref(user.uid).listAll().then( (res)=>{
			res.items.forEach(i=>{
				const path=i.toString().split("/")
				const date=path[path.length-1].split(".")[0]
				dates.push(date)
			})
			dates.sort()
			let prevDay=null
			dates.forEach(date=>{
				const day=date.split(" ")[0]
				if(prevDay!=day){
					const p = document.createElement('h5');
					p.innerHTML = "<br />Date : "+day+"<br />"+"Time :";
					p.className="text-light m-1"
					im.appendChild(p)
				}
				prevDay=day
				const t = document.createTextNode(date.split(" ")[1]);
				const btn = document.createElement("BUTTON")
				btn.type="button"
				btn.className="btn btn-secondary m-1";
				btn.appendChild(t);
				im.appendChild(btn);
				btn.onclick=()=>playAudioFrom(date);
			})
			im.className="bg-image scrollable"
			im.style="background-image: url('20210730_171708_2.jpg');background-size: cover;  background-position: center center; height:100vh; overflow-y: scroll"
		})
	})
	
}
function pauseAudio(){
	const audio = document.getElementById("myAudio"); 
	audio.pause();  
}

function create(){
	const email=document.getElementById("email").value
	const pass=document.getElementById("password").value
	firebase.auth().createUserWithEmailAndPassword(email, pass)
	.catch((error) => {
    const errorCode = error.code;
    const errorMessage = error.message;
	window.alert(errorMessage)
 });
}

function login(){
	const email=document.getElementById("email").value
	const pass=document.getElementById("password").value
	firebase.auth().signInWithEmailAndPassword(email, pass)
	  .catch((error) => {
		const errorCode = error.code;
		const errorMessage = error.message;
		window.alert(errorMessage)
	});
	
}
function logout(){
	firebase.auth().signOut()
}